#!/usr/bin/env ruby
# Lightweight playable header with rolling input — minimal footprint

require 'json'
require 'time'

module OsuMegamix
  VERSION = "1.a demo light"
  ASSET_DIR = "./assets"
  BUILD_DIR = "./builddir"

  LOW_POWER = ENV['LOW_POWER'] == '1'
  HANDHELD  = ENV['HANDHELD'] == '1'

  # Rolling input prototype — minimal
  module RollingInput
    @history = []

    def self.add_input(time, x, y)
      @history << {time: time, x: x, y: y}
      @history.shift if @history.size > 10
    end

    def self.current
      @history.last
    end
  end

  def self.run
    puts "[#{VERSION}] Starting demo load..."
    load_assets
    load_inputs
    load_timing
    run_demo
    puts "[#{VERSION}] Demo complete!"
  end

  def self.load_assets
    files = Dir["#{ASSET_DIR}/*"]
    puts "[Assets] #{files.size} files loaded"
  end

  def self.load_inputs
    puts "[Inputs] Devices active (LOW_POWER=#{LOW_POWER}, HANDHELD=#{HANDHELD})"
  end

  def self.load_timing
    puts "[Timing] Engine ready"
  end

  def self.run_demo
    beatmap = "#{ASSET_DIR}/test_beatmap.json"
    return puts "[Demo] No beatmap found" unless File.exist?(beatmap)

    data = JSON.parse(File.read(beatmap))
    puts "[Demo] Playing beatmap: #{data['title']}"

    start = Time.now
    data['notes'].each do |note|
      sleep_time = note['time']/1000.0 - (Time.now - start)
      sleep(sleep_time) if sleep_time > 0

      RollingInput.add_input(note['time'], note['x'], note['y'])
      state = RollingInput.current
      puts "[Hit] (#{note['x']},#{note['y']}) @ #{note['time']}ms | Rolling: #{state}"
    end
  end
end

OsuMegamix.run
