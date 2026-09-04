#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>

#include <moveit/robot_model_loader/robot_model_loader.hpp>
#include <moveit/planning_scene/planning_scene.hpp>
#include <moveit/robot_state/robot_state.hpp>
#include <moveit/collision_detection/collision_common.hpp>
#include <moveit_msgs/msg/collision_object.hpp>
#include <shape_msgs/msg/solid_primitive.hpp>
#include <geometry_msgs/msg/pose.hpp>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <limits>
#include <map>
#include <queue>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace fs = std::filesystem;

namespace
{
constexpr double kPi = 3.14159265358979323846;

double radToDeg(const double rad)
{
  return rad * 180.0 / kPi;
}

std::string csvEscape(const std::string& input)
{
  if (input.find_first_of(",\"\n") == std::string::npos)
    return input;
  std::string out = "\"";
  for (const char c : input)
  {
    if (c == '\"')
      out += "\"\"";
    else
      out += c;
  }
  out += "\"";
  return out;
}

std::string expandUser(const std::string& path)
{
  if (path.empty() || path[0] != '~')
    return path;
  const char* home = std::getenv("HOME");
  if (!home)
    return path;
  if (path.size() == 1)
    return std::string(home);
  if (path[1] == '/')
    return std::string(home) + path.substr(1);
  return path;
}

std::vector<double> makeAxis(const double minimum, const double maximum, const double step)
{
  if (!(step > 0.0) || maximum < minimum)
    throw std::invalid_argument("Invalid scan axis bounds or step");
  std::vector<double> values;
  for (double value = minimum; value <= maximum + step * 1e-8; value += step)
    values.push_back(std::min(value, maximum));
  if (values.empty() || std::abs(values.back() - maximum) > 1e-9)
    values.push_back(maximum);
  return values;
}

std::pair<double, double> solveLinearCommandRange(
  const double zero_deg, const double coefficient_deg_per_rad,
  const double command_min_deg, const double command_max_deg)
{
  if (std::abs(coefficient_deg_per_rad) < 1e-12)
    return { -std::numeric_limits<double>::infinity(), std::numeric_limits<double>::infinity() };
  const double a = (command_min_deg - zero_deg) / coefficient_deg_per_rad;
  const double b = (command_max_deg - zero_deg) / coefficient_deg_per_rad;
  return { std::min(a, b), std::max(a, b) };
}
}  // namespace

class SafeRegionGenerator : public rclcpp::Node
{
public:
  SafeRegionGenerator() : Node("safe_region_generator")
  {
    declareParameters();
    status_pub_ = create_publisher<std_msgs::msg::String>("~/status", 10);
    timer_ = create_wall_timer(std::chrono::milliseconds(100), [this]() {
      timer_->cancel();
      runOnce();
    });
  }

private:
  struct Sample
  {
    double q1{ 0.0 };
    double q2{ 0.0 };
    double q3{ 0.0 };
    double lift_cmd{ 0.0 };
    double tilt_cmd{ 0.0 };
    double grip_cmd{ 0.0 };
    bool safe{ false };
    bool connected{ false };
    std::string reason;
    std::string contacts;
  };

  struct Evaluation
  {
    bool safe{ false };
    double lift_cmd{ 0.0 };
    double tilt_cmd{ 0.0 };
    double grip_cmd{ 0.0 };
    std::string reason;
    std::string contacts;
  };

  void declareParameters()
  {
    declare_parameter<std::string>("output_directory", "~/MacRobot/data/safe_region");
    declare_parameter<std::string>("robot_model_mode", "reduced");
    declare_parameter<std::string>("model_revision", "unknown");
    declare_parameter<double>("q1_min", -1.0);
    declare_parameter<double>("q1_max", 1.0);
    declare_parameter<double>("q2_min", -1.30);
    declare_parameter<double>("q2_max", 1.30);
    declare_parameter<double>("q3_min", 0.0);
    declare_parameter<double>("q3_max", kPi / 2.0);
    declare_parameter<double>("q1_step_rad", 0.0872664626);
    declare_parameter<double>("q2_step_rad", 0.0872664626);
    declare_parameter<double>("q3_step_rad", 0.0872664626);
    declare_parameter<double>("home_q1", 0.0);
    declare_parameter<double>("home_q2", 0.0);
    declare_parameter<double>("home_q3", 0.0);

    declare_parameter<double>("lift_zero_deg", 90.0);
    declare_parameter<double>("lift_sign", 1.0);
    declare_parameter<double>("lift_model_multiplier", 2.0);
    declare_parameter<double>("lift_command_min_deg", 0.0);
    declare_parameter<double>("lift_command_max_deg", 180.0);

    declare_parameter<double>("tilt_zero_deg", 90.0);
    declare_parameter<double>("tilt_sign", 1.0);
    declare_parameter<double>("tilt_model_multiplier", -2.0);
    declare_parameter<double>("tilt_command_min_deg", 0.0);
    declare_parameter<double>("tilt_command_max_deg", 180.0);

    declare_parameter<double>("gripper_zero_deg", 0.0);
    declare_parameter<double>("gripper_sign", 1.0);
    declare_parameter<double>("gripper_model_multiplier", 2.0);
    declare_parameter<double>("gripper_command_min_deg", 0.0);
    declare_parameter<double>("gripper_command_max_deg", 180.0);

    declare_parameter<int>("edge_subsamples", 1);
    declare_parameter<bool>("include_floor", true);
    declare_parameter<double>("floor_z", 0.0);
    declare_parameter<double>("floor_size_x", 2.0);
    declare_parameter<double>("floor_size_y", 2.0);
    declare_parameter<double>("floor_thickness", 0.02);
    declare_parameter<std::vector<std::string>>(
      "floor_allowed_links", std::vector<std::string>{ "base_link" });
    declare_parameter<int>("max_contacts", 100);
    declare_parameter<bool>("shutdown_when_done", true);
  }

  template <typename T>
  T p(const std::string& name) const
  {
    return get_parameter(name).get_value<T>();
  }

  void publishStatus(const std::string& event, const std::string& detail = "")
  {
    std_msgs::msg::String msg;
    std::ostringstream out;
    out << "{\"event\":\"" << event << "\"";
    if (!detail.empty())
      out << ",\"detail\":\"" << detail << "\"";
    out << "}";
    msg.data = out.str();
    status_pub_->publish(msg);
  }

  void runOnce()
  {
    try
    {
      publishStatus("starting");
      loadParameters();

      model_loader_ = std::make_shared<robot_model_loader::RobotModelLoader>(
        shared_from_this(), "robot_description", false);
      robot_model_ = model_loader_->getModel();
      if (!robot_model_)
        throw std::runtime_error("MoveIt could not load robot_description/robot_description_semantic");

      const auto& variable_names = robot_model_->getVariableNames();
      const std::vector<std::string> required_variables = requiredVariables();
      for (const auto& name : required_variables)
      {
        if (std::find(variable_names.begin(), variable_names.end(), name) == variable_names.end())
          throw std::runtime_error("Robot model does not contain variable: " + name +
                                   " (robot_model_mode=" + robot_model_mode_ + ")");
      }

      scene_ = std::make_shared<planning_scene::PlanningScene>(robot_model_);
      if (include_floor_)
        addFloor();

      q1_values_ = makeAxis(q1_min_, q1_max_, q1_step_);
      q2_values_ = makeAxis(q2_min_, q2_max_, q2_step_);
      q3_values_ = makeAxis(q3_min_, q3_max_, q3_step_);
      const std::size_t total = q1_values_.size() * q2_values_.size() * q3_values_.size();
      samples_.resize(total);

      RCLCPP_INFO(get_logger(), "Scanning %zu states (%zu x %zu x %zu)", total, q1_values_.size(),
                  q2_values_.size(), q3_values_.size());
      publishStatus("scanning", std::to_string(total));

      std::size_t safe_count = 0;
      for (std::size_t i = 0; i < q1_values_.size(); ++i)
      {
        for (std::size_t j = 0; j < q2_values_.size(); ++j)
        {
          for (std::size_t k = 0; k < q3_values_.size(); ++k)
          {
            const auto index = flatIndex(i, j, k);
            auto& sample = samples_[index];
            sample.q1 = q1_values_[i];
            sample.q2 = q2_values_[j];
            sample.q3 = q3_values_[k];
            const Evaluation result = evaluate(sample.q1, sample.q2, sample.q3, true);
            sample.safe = result.safe;
            sample.lift_cmd = result.lift_cmd;
            sample.tilt_cmd = result.tilt_cmd;
            sample.grip_cmd = result.grip_cmd;
            sample.reason = result.reason;
            sample.contacts = result.contacts;
            ++reason_counts_[sample.reason];
            if (sample.safe)
              ++safe_count;
          }
        }
        if ((i + 1) % 4 == 0 || i + 1 == q1_values_.size())
          RCLCPP_INFO(get_logger(), "Scan progress: %zu/%zu q1 slices", i + 1, q1_values_.size());
      }

      const std::size_t connected_count = findConnectedComponent();
      writeOutputs(safe_count, connected_count);

      std::ostringstream detail;
      detail << "safe=" << safe_count << ",connected=" << connected_count;
      publishStatus("completed", detail.str());
      RCLCPP_INFO(get_logger(), "Completed. Safe: %zu, connected-to-home: %zu", safe_count, connected_count);
    }
    catch (const std::exception& ex)
    {
      RCLCPP_ERROR(get_logger(), "Safe-region generation failed: %s", ex.what());
      publishStatus("error", ex.what());
    }

    if (shutdown_when_done_)
      rclcpp::shutdown();
  }

  void loadParameters()
  {
    output_directory_ = fs::path(expandUser(p<std::string>("output_directory")));
    robot_model_mode_ = p<std::string>("robot_model_mode");
    model_revision_ = p<std::string>("model_revision");
    if (robot_model_mode_ != "serial_2r" && robot_model_mode_ != "reduced" && robot_model_mode_ != "full_mapped")
      throw std::invalid_argument("robot_model_mode must be serial_2r, reduced, or full_mapped");
    q1_min_ = p<double>("q1_min"); q1_max_ = p<double>("q1_max");
    q2_min_ = p<double>("q2_min"); q2_max_ = p<double>("q2_max");
    q3_min_ = p<double>("q3_min"); q3_max_ = p<double>("q3_max");
    q1_step_ = p<double>("q1_step_rad"); q2_step_ = p<double>("q2_step_rad");
    q3_step_ = p<double>("q3_step_rad");
    home_q1_ = p<double>("home_q1"); home_q2_ = p<double>("home_q2"); home_q3_ = p<double>("home_q3");

    lift_zero_ = p<double>("lift_zero_deg"); lift_sign_ = p<double>("lift_sign");
    lift_multiplier_ = p<double>("lift_model_multiplier");
    lift_min_cmd_ = p<double>("lift_command_min_deg"); lift_max_cmd_ = p<double>("lift_command_max_deg");
    tilt_zero_ = p<double>("tilt_zero_deg"); tilt_sign_ = p<double>("tilt_sign");
    tilt_multiplier_ = p<double>("tilt_model_multiplier");
    tilt_min_cmd_ = p<double>("tilt_command_min_deg"); tilt_max_cmd_ = p<double>("tilt_command_max_deg");
    grip_zero_ = p<double>("gripper_zero_deg"); grip_sign_ = p<double>("gripper_sign");
    grip_multiplier_ = p<double>("gripper_model_multiplier");
    grip_min_cmd_ = p<double>("gripper_command_min_deg"); grip_max_cmd_ = p<double>("gripper_command_max_deg");

    edge_subsamples_ = static_cast<int>(get_parameter("edge_subsamples").as_int());
    include_floor_ = p<bool>("include_floor");
    floor_z_ = p<double>("floor_z"); floor_size_x_ = p<double>("floor_size_x");
    floor_size_y_ = p<double>("floor_size_y"); floor_thickness_ = p<double>("floor_thickness");
    floor_allowed_links_ = p<std::vector<std::string>>("floor_allowed_links");
    max_contacts_ = static_cast<int>(get_parameter("max_contacts").as_int());
    shutdown_when_done_ = p<bool>("shutdown_when_done");
  }

  std::vector<std::string> requiredVariables() const
  {
    return { "arm_lift_joint", "wrist_pitch_joint", "gripper_joint" };
  }

  void setStateFromLogical(
    moveit::core::RobotState& state, const double q1, const double q2, const double q3) const
  {
    state.setToDefaultValues();
    state.setVariablePosition("arm_lift_joint", q1);
    state.setVariablePosition("wrist_pitch_joint", q2);
    state.setVariablePosition("gripper_joint", q3);
  }

  void addFloor()
  {
    moveit_msgs::msg::CollisionObject floor;
    floor.header.frame_id = robot_model_->getModelFrame();
    floor.id = "floor";
    floor.operation = moveit_msgs::msg::CollisionObject::ADD;

    shape_msgs::msg::SolidPrimitive primitive;
    primitive.type = shape_msgs::msg::SolidPrimitive::BOX;
    primitive.dimensions = { floor_size_x_, floor_size_y_, floor_thickness_ };
    geometry_msgs::msg::Pose pose;
    pose.orientation.w = 1.0;
    pose.position.z = floor_z_ - floor_thickness_ / 2.0;
    floor.primitives.push_back(primitive);
    floor.primitive_poses.push_back(pose);
    if (!scene_->processCollisionObjectMsg(floor))
      throw std::runtime_error("Failed to add floor collision object");

    auto& acm = scene_->getAllowedCollisionMatrixNonConst();
    for (const auto& link : floor_allowed_links_)
      acm.setEntry(link, floor.id, true);
  }

  Evaluation evaluate(const double q1, const double q2, const double q3, const bool accumulate_stats)
  {
    Evaluation out;
    out.lift_cmd = lift_zero_ + lift_sign_ * radToDeg(lift_multiplier_ * q1);
    out.tilt_cmd = tilt_zero_ + tilt_sign_ * radToDeg(tilt_multiplier_ * q2);
    out.grip_cmd = grip_zero_ + grip_sign_ * radToDeg(grip_multiplier_ * q3);

    if (q1 < q1_min_ || q1 > q1_max_ || q2 < q2_min_ || q2 > q2_max_ || q3 < q3_min_ || q3 > q3_max_)
    {
      out.reason = "logical_joint_limit";
      return out;
    }
    if (out.lift_cmd < lift_min_cmd_ || out.lift_cmd > lift_max_cmd_)
    {
      out.reason = "lift_servo_limit";
      return out;
    }
    if (out.tilt_cmd < tilt_min_cmd_ || out.tilt_cmd > tilt_max_cmd_)
    {
      out.reason = "tilt_servo_limit";
      return out;
    }
    if (out.grip_cmd < grip_min_cmd_ || out.grip_cmd > grip_max_cmd_)
    {
      out.reason = "gripper_servo_limit";
      return out;
    }

    moveit::core::RobotState state(robot_model_);
    setStateFromLogical(state, q1, q2, q3);
    state.update(true);
    if (!state.satisfiesBounds())
    {
      out.reason = "moveit_joint_bounds";
      return out;
    }

    collision_detection::CollisionRequest request;
    request.contacts = true;
    request.max_contacts = static_cast<std::size_t>(std::max(1, max_contacts_));
    request.max_contacts_per_pair = 1;
    collision_detection::CollisionResult result;
    scene_->checkCollision(request, result, state, scene_->getAllowedCollisionMatrix());
    if (result.collision)
    {
      out.reason = "collision";
      std::set<std::string> pairs;
      for (const auto& entry : result.contacts)
      {
        std::string a = entry.first.first;
        std::string b = entry.first.second;
        if (b < a)
          std::swap(a, b);
        const std::string pair = a + "|" + b;
        pairs.insert(pair);
        if (accumulate_stats)
          ++contact_pair_counts_[pair];
      }
      std::ostringstream text;
      bool first = true;
      for (const auto& pair : pairs)
      {
        if (!first) text << ';';
        text << pair;
        first = false;
      }
      out.contacts = text.str();
      return out;
    }

    out.safe = true;
    out.reason = "safe";
    return out;
  }

  std::size_t flatIndex(const std::size_t i, const std::size_t j, const std::size_t k) const
  {
    return (i * q2_values_.size() + j) * q3_values_.size() + k;
  }

  bool edgeSafe(const Sample& a, const Sample& b)
  {
    for (int n = 1; n <= edge_subsamples_; ++n)
    {
      const double t = static_cast<double>(n) / static_cast<double>(edge_subsamples_ + 1);
      const Evaluation result = evaluate(
        a.q1 + t * (b.q1 - a.q1),
        a.q2 + t * (b.q2 - a.q2),
        a.q3 + t * (b.q3 - a.q3), false);
      if (!result.safe)
        return false;
    }
    return true;
  }

  std::size_t findConnectedComponent()
  {
    std::size_t seed = samples_.size();
    double best_distance = std::numeric_limits<double>::infinity();
    for (std::size_t index = 0; index < samples_.size(); ++index)
    {
      if (!samples_[index].safe)
        continue;
      const auto& s = samples_[index];
      const double d = std::pow((s.q1 - home_q1_) / q1_step_, 2) +
                       std::pow((s.q2 - home_q2_) / q2_step_, 2) +
                       std::pow((s.q3 - home_q3_) / q3_step_, 2);
      if (d < best_distance)
      {
        best_distance = d;
        seed = index;
      }
    }
    if (seed == samples_.size())
      return 0;

    std::queue<std::tuple<std::size_t, std::size_t, std::size_t>> queue;
    const std::size_t i0 = seed / (q2_values_.size() * q3_values_.size());
    const std::size_t rem = seed % (q2_values_.size() * q3_values_.size());
    const std::size_t j0 = rem / q3_values_.size();
    const std::size_t k0 = rem % q3_values_.size();
    samples_[seed].connected = true;
    queue.emplace(i0, j0, k0);
    std::size_t count = 1;
    const int directions[6][3] = { { 1, 0, 0 }, { -1, 0, 0 }, { 0, 1, 0 },
                                   { 0, -1, 0 }, { 0, 0, 1 }, { 0, 0, -1 } };

    while (!queue.empty())
    {
      const auto [i, j, k] = queue.front();
      queue.pop();
      const auto current_index = flatIndex(i, j, k);
      for (const auto& direction : directions)
      {
        const long ni = static_cast<long>(i) + direction[0];
        const long nj = static_cast<long>(j) + direction[1];
        const long nk = static_cast<long>(k) + direction[2];
        if (ni < 0 || nj < 0 || nk < 0 || ni >= static_cast<long>(q1_values_.size()) ||
            nj >= static_cast<long>(q2_values_.size()) || nk >= static_cast<long>(q3_values_.size()))
          continue;
        const auto next_index = flatIndex(static_cast<std::size_t>(ni), static_cast<std::size_t>(nj),
                                          static_cast<std::size_t>(nk));
        auto& next = samples_[next_index];
        if (!next.safe || next.connected)
          continue;
        if (edge_subsamples_ > 0 && !edgeSafe(samples_[current_index], next))
          continue;
        next.connected = true;
        ++count;
        queue.emplace(static_cast<std::size_t>(ni), static_cast<std::size_t>(nj),
                      static_cast<std::size_t>(nk));
      }
    }
    return count;
  }

  void writeOutputs(const std::size_t safe_count, const std::size_t connected_count)
  {
    fs::create_directories(output_directory_);
    writeSamplesCsv(output_directory_ / "safe_samples.csv", false);
    writeSamplesCsv(output_directory_ / "safe_connected_samples.csv", true);
    writeIntervalsCsv(output_directory_ / "safe_q2_intervals_by_q1_q3.csv");
    writeSummary(output_directory_ / "safe_region_summary.yaml", safe_count, connected_count);
  }

  void writeSamplesCsv(const fs::path& path, const bool connected_only) const
  {
    std::ofstream file(path);
    if (!file)
      throw std::runtime_error("Cannot write " + path.string());
    file << "q1_rad,q2_rad,q3_rad,shoulder_servo_deg,wrist_servo_deg,gripper_servo_deg,safe,connected,reason,contacts\n";
    file << std::setprecision(10);
    for (const auto& sample : samples_)
    {
      if (connected_only && !sample.connected)
        continue;
      file << sample.q1 << ',' << sample.q2 << ',' << sample.q3 << ',' << sample.lift_cmd << ','
           << sample.tilt_cmd << ',' << sample.grip_cmd << ',' << (sample.safe ? 1 : 0) << ','
           << (sample.connected ? 1 : 0) << ',' << csvEscape(sample.reason) << ','
           << csvEscape(sample.contacts) << '\n';
    }
  }

  void writeIntervalsCsv(const fs::path& path) const
  {
    std::ofstream file(path);
    if (!file)
      throw std::runtime_error("Cannot write " + path.string());
    file << "q1_rad,q3_rad,segment,q2_min_rad,q2_max_rad,sample_count\n";
    file << std::setprecision(10);
    for (std::size_t i = 0; i < q1_values_.size(); ++i)
    {
      for (std::size_t k = 0; k < q3_values_.size(); ++k)
      {
        int segment = 0;
        std::size_t j = 0;
        while (j < q2_values_.size())
        {
          while (j < q2_values_.size() && !samples_[flatIndex(i, j, k)].connected)
            ++j;
          if (j >= q2_values_.size())
            break;
          const std::size_t start = j;
          while (j + 1 < q2_values_.size() && samples_[flatIndex(i, j + 1, k)].connected)
            ++j;
          const std::size_t end = j;
          file << q1_values_[i] << ',' << q3_values_[k] << ',' << segment++ << ','
               << q2_values_[start] << ',' << q2_values_[end] << ',' << (end - start + 1) << '\n';
          ++j;
        }
      }
    }
  }

  void writeSummary(const fs::path& path, const std::size_t safe_count, const std::size_t connected_count) const
  {
    std::ofstream file(path);
    if (!file)
      throw std::runtime_error("Cannot write " + path.string());
    const std::size_t total = samples_.size();
    file << std::setprecision(10);
    file << "generator: macrobot_safe_region\n";
    file << "robot_model: " << robot_model_->getName() << "\n";
    file << "robot_model_mode: " << robot_model_mode_ << "\n";
    file << "model_revision: " << model_revision_ << "\n";
    file << "output_directory: " << output_directory_.string() << "\n";
    file << "counts:\n";
    file << "  total: " << total << "\n";
    file << "  safe: " << safe_count << "\n";
    file << "  connected_to_home: " << connected_count << "\n";
    file << "  safe_fraction: " << (total ? static_cast<double>(safe_count) / total : 0.0) << "\n";
    file << "scan:\n";
    file << "  q1: {min: " << q1_min_ << ", max: " << q1_max_ << ", step: " << q1_step_ << "}\n";
    file << "  q2: {min: " << q2_min_ << ", max: " << q2_max_ << ", step: " << q2_step_ << "}\n";
    file << "  q3: {min: " << q3_min_ << ", max: " << q3_max_ << ", step: " << q3_step_ << "}\n";
    file << "initial_servo_commands_deg:\n";
    file << "  left_shoulder_mg996r: " << lift_zero_ << "\n";
    file << "  right_wrist_mg996r: " << tilt_zero_ << "\n";
    file << "  gripper_mg90s_open: " << grip_zero_ << "\n";
    file << "  gripper_mg90s_closed: "
         << (grip_zero_ + grip_sign_ * radToDeg(grip_multiplier_ * q3_max_)) << "\n";

    const auto q1_servo_range = solveLinearCommandRange(
      lift_zero_, lift_sign_ * lift_multiplier_ * 180.0 / kPi, lift_min_cmd_, lift_max_cmd_);
    const auto pitch_servo_range = solveLinearCommandRange(
      tilt_zero_, tilt_sign_ * tilt_multiplier_ * 180.0 / kPi, tilt_min_cmd_, tilt_max_cmd_);
    const auto q3_servo_range = solveLinearCommandRange(
      grip_zero_, grip_sign_ * grip_multiplier_ * 180.0 / kPi, grip_min_cmd_, grip_max_cmd_);
    file << "actuator_implied_logical_ranges_rad:\n";
    file << "  q1_from_left_tilt_servo: [" << q1_servo_range.first << ", " << q1_servo_range.second << "]\n";
    file << "  q2_from_wrist_servo: [" << pitch_servo_range.first << ", " << pitch_servo_range.second << "]\n";
    file << "  q3_from_gripper_servo: [" << q3_servo_range.first << ", " << q3_servo_range.second << "]\n";

    bool have_connected = false;
    double min_q1 = std::numeric_limits<double>::infinity(), max_q1 = -min_q1;
    double min_q2 = std::numeric_limits<double>::infinity(), max_q2 = -min_q2;
    double min_q3 = std::numeric_limits<double>::infinity(), max_q3 = -min_q3;
    for (const auto& s : samples_)
    {
      if (!s.connected) continue;
      have_connected = true;
      min_q1 = std::min(min_q1, s.q1); max_q1 = std::max(max_q1, s.q1);
      min_q2 = std::min(min_q2, s.q2); max_q2 = std::max(max_q2, s.q2);
      min_q3 = std::min(min_q3, s.q3); max_q3 = std::max(max_q3, s.q3);
    }
    file << "connected_component_bounds_rad:\n";
    if (have_connected)
    {
      file << "  q1: [" << min_q1 << ", " << max_q1 << "]\n";
      file << "  q2: [" << min_q2 << ", " << max_q2 << "]\n";
      file << "  q3: [" << min_q3 << ", " << max_q3 << "]\n";
    }
    else
    {
      file << "  error: no safe component connected to home\n";
    }
    file << "reject_reason_counts:\n";
    for (const auto& entry : reason_counts_)
      file << "  " << entry.first << ": " << entry.second << "\n";
    file << "top_collision_pairs:\n";
    std::vector<std::pair<std::string, std::size_t>> pairs(contact_pair_counts_.begin(), contact_pair_counts_.end());
    std::sort(pairs.begin(), pairs.end(), [](const auto& a, const auto& b) { return a.second > b.second; });
    const std::size_t limit = std::min<std::size_t>(pairs.size(), 20);
    for (std::size_t i = 0; i < limit; ++i)
      file << "  - {pair: \"" << pairs[i].first << "\", count: " << pairs[i].second << "}\n";
  }

  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr status_pub_;
  robot_model_loader::RobotModelLoaderPtr model_loader_;
  moveit::core::RobotModelPtr robot_model_;
  planning_scene::PlanningScenePtr scene_;

  fs::path output_directory_;
  std::string robot_model_mode_{ "reduced" };
  std::string model_revision_{ "unknown" };
  double q1_min_, q1_max_, q2_min_, q2_max_, q3_min_, q3_max_;
  double q1_step_, q2_step_, q3_step_;
  double home_q1_, home_q2_, home_q3_;
  double lift_zero_, lift_sign_, lift_multiplier_, lift_min_cmd_, lift_max_cmd_;
  double tilt_zero_, tilt_sign_, tilt_multiplier_, tilt_min_cmd_, tilt_max_cmd_;
  double grip_zero_, grip_sign_, grip_multiplier_, grip_min_cmd_, grip_max_cmd_;
  int edge_subsamples_{ 1 };
  bool include_floor_{ true };
  double floor_z_{ 0.0 }, floor_size_x_{ 2.0 }, floor_size_y_{ 2.0 }, floor_thickness_{ 0.02 };
  std::vector<std::string> floor_allowed_links_;
  int max_contacts_{ 100 };
  bool shutdown_when_done_{ true };

  std::vector<double> q1_values_, q2_values_, q3_values_;
  std::vector<Sample> samples_;
  std::map<std::string, std::size_t> reason_counts_;
  std::map<std::string, std::size_t> contact_pair_counts_;
};

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SafeRegionGenerator>());
  if (rclcpp::ok())
    rclcpp::shutdown();
  return 0;
}
