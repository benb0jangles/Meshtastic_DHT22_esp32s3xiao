#!/usr/bin/env python3
"""
Meshtastic Device Configuration GUI

A simple GUI tool to configure Meshtastic device settings before or after
flashing the DHT22 custom firmware.

Supports:
- Setting device name and short name
- Configuring LoRa region, modem preset, TX power
- Setting device role
- Enabling DHT22 telemetry
- Saving/loading configuration presets
- Exporting pre-install configurations (JSON)
- Generating automated setup scripts (Bash/Batch)

Pre-Install Configuration Features:
- Save configurations as structured JSON files
- Export as executable setup scripts for fresh devices
- Automatically generates both Windows (.bat) and Linux/Mac (.sh) scripts
- Scripts include connection testing and error handling
- Perfect for setting up multiple devices with identical configurations

Requirements:
    pip install meshtastic

Usage:
    python meshtastic_config_gui.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import subprocess
import sys

# Default configuration values
DEFAULT_CONFIG = {
    "device_name": "DHT22 Node",
    "short_name": "DHT",
    "region": "EU_868",
    "modem_preset": "LONG_FAST",
    "tx_power": 22,
    "device_role": "CLIENT",
    "hop_limit": 7,
    "telemetry_enabled": True,
    "telemetry_interval": 300,
    "bluetooth_enabled": True,
    "wifi_enabled": False,
    "wifi_ssid": "",
    "wifi_password": ""
}

# Configuration options
REGIONS = [
    ("EU_868", "Europe/UK (868 MHz)"),
    ("US", "USA/Canada (915 MHz)"),
    ("AU_915", "Australia (915 MHz)"),
    ("CN", "China (470 MHz)"),
    ("JP", "Japan (920 MHz)"),
    ("KR", "Korea (920 MHz)"),
    ("TW", "Taiwan (923 MHz)"),
    ("IN", "India (865 MHz)"),
    ("NZ_865", "New Zealand (865 MHz)"),
    ("RU", "Russia (868 MHz)"),
    ("UA_868", "Ukraine (868 MHz)"),
]

MODEM_PRESETS = [
    ("LONG_SLOW", "Long Slow (~50+ km, very slow)"),
    ("LONG_FAST", "Long Fast (~30 km, moderate) - Recommended"),
    ("LONG_MODERATE", "Long Moderate (~20 km, good speed)"),
    ("VERY_LONG_SLOW", "Very Long Slow (maximum range)"),
    ("MEDIUM_FAST", "Medium Fast (~10 km)"),
    ("MEDIUM_SLOW", "Medium Slow (~15 km)"),
    ("SHORT_FAST", "Short Fast (~5 km, urban)"),
    ("SHORT_SLOW", "Short Slow (~8 km)"),
]

DEVICE_ROLES = [
    ("CLIENT", "Client - Standard mobile operation"),
    ("CLIENT_MUTE", "Client Mute - Receive only"),
    ("ROUTER", "Router - Forward messages only"),
    ("ROUTER_CLIENT", "Router Client - Router + client features"),
    ("REPEATER", "Repeater - Simple message forwarding"),
    ("TRACKER", "Tracker - GPS tracking focus"),
    ("SENSOR", "Sensor - Low power remote sensing"),
    ("TAK", "TAK - ATAK/WinTAK integration"),
    ("CLIENT_HIDDEN", "Client Hidden - Hidden from node list"),
    ("LOST_AND_FOUND", "Lost and Found - Recovery mode"),
]


class MeshtasticConfigGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Meshtastic DHT22 Firmware Configuration")
        self.root.geometry("700x820")
        self.root.resizable(True, True)

        # Configuration storage
        self.config = DEFAULT_CONFIG.copy()
        self.config_file = os.path.join(os.path.dirname(__file__), "device_config.json")

        # Load saved config if exists
        self.load_config()

        # Create main frame with scrollbar
        self.create_widgets()

    def create_widgets(self):
        # Create main canvas with scrollbar
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Main container
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Meshtastic DHT22 Configuration",
                               font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 10))

        # Device Identity Section
        identity_frame = ttk.LabelFrame(main_frame, text="Device Identity", padding="10")
        identity_frame.pack(fill="x", pady=5)

        # Device Name
        ttk.Label(identity_frame, text="Device Name (Long Name):").grid(row=0, column=0, sticky="w", pady=2)
        self.device_name_var = tk.StringVar(value=self.config["device_name"])
        self.device_name_entry = ttk.Entry(identity_frame, textvariable=self.device_name_var, width=40)
        self.device_name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        # Short Name
        ttk.Label(identity_frame, text="Short Name (max 4 chars):").grid(row=1, column=0, sticky="w", pady=2)
        self.short_name_var = tk.StringVar(value=self.config["short_name"])
        self.short_name_entry = ttk.Entry(identity_frame, textvariable=self.short_name_var, width=10)
        self.short_name_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        identity_frame.columnconfigure(1, weight=1)

        # LoRa Configuration Section
        lora_frame = ttk.LabelFrame(main_frame, text="LoRa Configuration", padding="10")
        lora_frame.pack(fill="x", pady=5)

        # Region
        ttk.Label(lora_frame, text="Region:").grid(row=0, column=0, sticky="w", pady=2)
        self.region_var = tk.StringVar(value=self.config["region"])
        self.region_combo = ttk.Combobox(lora_frame, textvariable=self.region_var, width=35, state="readonly")
        self.region_combo["values"] = [f"{r[0]} - {r[1]}" for r in REGIONS]
        self.region_combo.set(f"{self.config['region']} - {dict(REGIONS).get(self.config['region'], '')}")
        self.region_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        # Region warning
        region_warning = ttk.Label(lora_frame, text="Use EU_868 for UK!",
                                  foreground="red", font=("Helvetica", 9, "bold"))
        region_warning.grid(row=0, column=2, padx=5)

        # Modem Preset
        ttk.Label(lora_frame, text="Modem Preset:").grid(row=1, column=0, sticky="w", pady=2)
        self.modem_var = tk.StringVar(value=self.config["modem_preset"])
        self.modem_combo = ttk.Combobox(lora_frame, textvariable=self.modem_var, width=35, state="readonly")
        self.modem_combo["values"] = [f"{m[0]} - {m[1]}" for m in MODEM_PRESETS]
        self.modem_combo.set(f"{self.config['modem_preset']} - {dict(MODEM_PRESETS).get(self.config['modem_preset'], '')}")
        self.modem_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        # TX Power
        ttk.Label(lora_frame, text="TX Power (dBm):").grid(row=2, column=0, sticky="w", pady=2)
        self.tx_power_var = tk.IntVar(value=self.config["tx_power"])
        self.tx_power_spin = ttk.Spinbox(lora_frame, from_=1, to=30, textvariable=self.tx_power_var, width=10)
        self.tx_power_spin.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        ttk.Label(lora_frame, text="(EU max: 27, recommended: 22)").grid(row=2, column=2, sticky="w")

        # Hop Limit
        ttk.Label(lora_frame, text="Hop Limit:").grid(row=3, column=0, sticky="w", pady=2)
        self.hop_limit_var = tk.IntVar(value=self.config["hop_limit"])
        self.hop_limit_spin = ttk.Spinbox(lora_frame, from_=1, to=7, textvariable=self.hop_limit_var, width=10)
        self.hop_limit_spin.grid(row=3, column=1, sticky="w", padx=5, pady=2)

        lora_frame.columnconfigure(1, weight=1)

        # Device Role Section
        role_frame = ttk.LabelFrame(main_frame, text="Device Role", padding="10")
        role_frame.pack(fill="x", pady=5)

        self.role_var = tk.StringVar(value=self.config["device_role"])
        self.role_combo = ttk.Combobox(role_frame, textvariable=self.role_var, width=50, state="readonly")
        self.role_combo["values"] = [f"{r[0]} - {r[1]}" for r in DEVICE_ROLES]
        self.role_combo.set(f"{self.config['device_role']} - {dict(DEVICE_ROLES).get(self.config['device_role'], '')}")
        self.role_combo.pack(fill="x")

        # DHT22 Telemetry Section
        telemetry_frame = ttk.LabelFrame(main_frame, text="DHT22 Telemetry", padding="10")
        telemetry_frame.pack(fill="x", pady=5)

        # Telemetry enabled
        self.telemetry_enabled_var = tk.BooleanVar(value=self.config["telemetry_enabled"])
        ttk.Checkbutton(telemetry_frame, text="Enable Environmental Telemetry (DHT22)",
                       variable=self.telemetry_enabled_var).grid(row=0, column=0, columnspan=2, sticky="w", pady=2)

        # Telemetry interval
        ttk.Label(telemetry_frame, text="Update Interval (seconds):").grid(row=1, column=0, sticky="w", pady=2)
        self.telemetry_interval_var = tk.IntVar(value=self.config["telemetry_interval"])
        self.telemetry_interval_spin = ttk.Spinbox(telemetry_frame, from_=60, to=3600,
                                                   textvariable=self.telemetry_interval_var, width=10)
        self.telemetry_interval_spin.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        # Connectivity Section
        conn_frame = ttk.LabelFrame(main_frame, text="Connectivity", padding="10")
        conn_frame.pack(fill="x", pady=5)

        # Bluetooth
        self.bluetooth_var = tk.BooleanVar(value=self.config["bluetooth_enabled"])
        ttk.Checkbutton(conn_frame, text="Enable Bluetooth",
                       variable=self.bluetooth_var).grid(row=0, column=0, sticky="w", pady=2)

        # WiFi
        self.wifi_var = tk.BooleanVar(value=self.config["wifi_enabled"])
        ttk.Checkbutton(conn_frame, text="Enable WiFi (ESP32-S3 only)",
                       variable=self.wifi_var, command=self.toggle_wifi).grid(row=1, column=0, sticky="w", pady=2)

        # WiFi SSID
        ttk.Label(conn_frame, text="WiFi SSID:").grid(row=2, column=0, sticky="w", pady=2)
        self.wifi_ssid_var = tk.StringVar(value=self.config["wifi_ssid"])
        self.wifi_ssid_entry = ttk.Entry(conn_frame, textvariable=self.wifi_ssid_var, width=30)
        self.wifi_ssid_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        # WiFi Password
        ttk.Label(conn_frame, text="WiFi Password:").grid(row=3, column=0, sticky="w", pady=2)
        self.wifi_pass_var = tk.StringVar(value=self.config["wifi_password"])
        self.wifi_pass_entry = ttk.Entry(conn_frame, textvariable=self.wifi_pass_var, width=30, show="*")
        self.wifi_pass_entry.grid(row=3, column=1, sticky="w", padx=5, pady=2)

        # Show/hide password button
        self.show_pass_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(conn_frame, text="Show", variable=self.show_pass_var,
                       command=self.toggle_password).grid(row=3, column=2, sticky="w")

        self.toggle_wifi()  # Set initial state

        # COM Port Section
        port_frame = ttk.LabelFrame(main_frame, text="Device Connection", padding="10")
        port_frame.pack(fill="x", pady=5)

        ttk.Label(port_frame, text="COM Port:").grid(row=0, column=0, sticky="w", pady=2)
        self.port_var = tk.StringVar(value="COM3")
        self.port_entry = ttk.Entry(port_frame, textvariable=self.port_var, width=15)
        self.port_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ttk.Button(port_frame, text="Detect Ports", command=self.detect_ports).grid(row=0, column=2, padx=5)
        ttk.Button(port_frame, text="Test Connection", command=self.test_connection).grid(row=0, column=3, padx=5)

        # Buttons Section
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=15)

        ttk.Button(button_frame, text="Save Config", command=self.save_config,
                  width=15).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Load Config", command=self.load_config_dialog,
                  width=15).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_defaults,
                  width=15).pack(side="left", padx=5)

        # Pre-Install Config Section
        preinstall_frame = ttk.Frame(main_frame)
        preinstall_frame.pack(fill="x", pady=5)

        ttk.Label(preinstall_frame, text="Pre-Install Configuration:",
                 font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(5, 2))

        preinstall_buttons = ttk.Frame(preinstall_frame)
        preinstall_buttons.pack(fill="x")

        ttk.Button(preinstall_buttons, text="Save as Pre-Install Config",
                  command=self.save_preinstall_config, width=22).pack(side="left", padx=5)
        ttk.Button(preinstall_buttons, text="Export Setup Script",
                  command=self.export_setup_script, width=18).pack(side="left", padx=5)

        # Apply Section
        apply_frame = ttk.Frame(main_frame)
        apply_frame.pack(fill="x", pady=5)

        ttk.Button(apply_frame, text="Apply to Device", command=self.apply_config,
                  width=20, style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(apply_frame, text="Generate CLI Commands", command=self.generate_commands,
                  width=20).pack(side="left", padx=5)
        ttk.Button(apply_frame, text="Export Commands", command=self.export_commands,
                  width=15).pack(side="left", padx=5)

        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(fill="x", side="bottom", pady=(10, 0))

        # Bind mouse wheel to canvas
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def toggle_wifi(self):
        """Enable/disable WiFi fields based on checkbox"""
        state = "normal" if self.wifi_var.get() else "disabled"
        self.wifi_ssid_entry.configure(state=state)
        self.wifi_pass_entry.configure(state=state)

    def toggle_password(self):
        """Show/hide WiFi password"""
        self.wifi_pass_entry.configure(show="" if self.show_pass_var.get() else "*")

    def detect_ports(self):
        """Detect available COM ports"""
        try:
            import serial.tools.list_ports
            ports = [p.device for p in serial.tools.list_ports.comports()]
            if ports:
                # Create popup with detected ports
                popup = tk.Toplevel(self.root)
                popup.title("Detected Ports")
                popup.geometry("300x200")

                ttk.Label(popup, text="Select a COM port:").pack(pady=10)

                listbox = tk.Listbox(popup, height=6)
                for port in ports:
                    listbox.insert(tk.END, port)
                listbox.pack(padx=20, pady=5, fill="both", expand=True)

                def select_port():
                    selection = listbox.curselection()
                    if selection:
                        self.port_var.set(ports[selection[0]])
                        popup.destroy()

                ttk.Button(popup, text="Select", command=select_port).pack(pady=10)
            else:
                messagebox.showinfo("Ports", "No COM ports detected.\nMake sure device is connected.")
        except ImportError:
            messagebox.showwarning("Missing Module",
                                  "pyserial not installed.\nRun: pip install pyserial")

    def test_connection(self):
        """Test connection to device"""
        port = self.port_var.get()
        self.status_var.set(f"Testing connection to {port}...")
        self.root.update()

        try:
            result = subprocess.run(
                ["meshtastic", "--port", port, "--info"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                messagebox.showinfo("Connection Test", f"Successfully connected to {port}!")
                self.status_var.set(f"Connected to {port}")
            else:
                messagebox.showerror("Connection Test",
                                    f"Failed to connect to {port}\n\n{result.stderr}")
                self.status_var.set("Connection failed")
        except FileNotFoundError:
            messagebox.showerror("Error",
                               "meshtastic CLI not found.\nRun: pip install meshtastic")
            self.status_var.set("meshtastic CLI not found")
        except subprocess.TimeoutExpired:
            messagebox.showerror("Timeout", "Connection timed out")
            self.status_var.set("Connection timeout")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
            self.status_var.set("Error")

    def get_current_config(self):
        """Get current configuration from GUI fields"""
        # Extract just the region/modem/role code from combo box
        region = self.region_combo.get().split(" - ")[0] if " - " in self.region_combo.get() else self.region_var.get()
        modem = self.modem_combo.get().split(" - ")[0] if " - " in self.modem_combo.get() else self.modem_var.get()
        role = self.role_combo.get().split(" - ")[0] if " - " in self.role_combo.get() else self.role_var.get()

        return {
            "device_name": self.device_name_var.get(),
            "short_name": self.short_name_var.get()[:4],  # Limit to 4 chars
            "region": region,
            "modem_preset": modem,
            "tx_power": self.tx_power_var.get(),
            "device_role": role,
            "hop_limit": self.hop_limit_var.get(),
            "telemetry_enabled": self.telemetry_enabled_var.get(),
            "telemetry_interval": self.telemetry_interval_var.get(),
            "bluetooth_enabled": self.bluetooth_var.get(),
            "wifi_enabled": self.wifi_var.get(),
            "wifi_ssid": self.wifi_ssid_var.get(),
            "wifi_password": self.wifi_pass_var.get()
        }

    def save_config(self):
        """Save configuration to JSON file"""
        config = self.get_current_config()
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.status_var.set(f"Configuration saved to {self.config_file}")
            messagebox.showinfo("Saved", "Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    def load_config(self):
        """Load configuration from JSON file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle new fields
                    self.config = {**DEFAULT_CONFIG, **loaded}
            except Exception:
                self.config = DEFAULT_CONFIG.copy()
        else:
            self.config = DEFAULT_CONFIG.copy()

    def load_config_dialog(self):
        """Open file dialog to load config"""
        filepath = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.path.dirname(self.config_file)
        )
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    loaded = json.load(f)
                    self.config = {**DEFAULT_CONFIG, **loaded}
                    self.update_gui_from_config()
                self.status_var.set(f"Loaded configuration from {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")

    def update_gui_from_config(self):
        """Update GUI fields from config"""
        self.device_name_var.set(self.config["device_name"])
        self.short_name_var.set(self.config["short_name"])

        # Update combo boxes
        region_desc = dict(REGIONS).get(self.config["region"], "")
        self.region_combo.set(f"{self.config['region']} - {region_desc}")

        modem_desc = dict(MODEM_PRESETS).get(self.config["modem_preset"], "")
        self.modem_combo.set(f"{self.config['modem_preset']} - {modem_desc}")

        role_desc = dict(DEVICE_ROLES).get(self.config["device_role"], "")
        self.role_combo.set(f"{self.config['device_role']} - {role_desc}")

        self.tx_power_var.set(self.config["tx_power"])
        self.hop_limit_var.set(self.config["hop_limit"])
        self.telemetry_enabled_var.set(self.config["telemetry_enabled"])
        self.telemetry_interval_var.set(self.config["telemetry_interval"])
        self.bluetooth_var.set(self.config["bluetooth_enabled"])
        self.wifi_var.set(self.config["wifi_enabled"])
        self.wifi_ssid_var.set(self.config["wifi_ssid"])
        self.wifi_pass_var.set(self.config["wifi_password"])
        self.toggle_wifi()

    def reset_defaults(self):
        """Reset all fields to default values"""
        if messagebox.askyesno("Reset", "Reset all settings to defaults?"):
            self.config = DEFAULT_CONFIG.copy()
            self.update_gui_from_config()
            self.status_var.set("Reset to default values")

    def generate_cli_commands(self):
        """Generate meshtastic CLI commands"""
        config = self.get_current_config()
        port = self.port_var.get()

        commands = []
        commands.append(f"# Meshtastic CLI Configuration Commands")
        commands.append(f"# Generated for port: {port}")
        commands.append("")
        commands.append("# Device Identity")
        commands.append(f'meshtastic --port {port} --set-owner "{config["device_name"]}"')
        commands.append(f'meshtastic --port {port} --set-owner-short "{config["short_name"]}"')
        commands.append("")
        commands.append("# LoRa Configuration")
        commands.append(f"meshtastic --port {port} --set lora.region {config['region']}")
        commands.append(f"meshtastic --port {port} --set lora.modem_preset {config['modem_preset']}")
        commands.append(f"meshtastic --port {port} --set lora.tx_power {config['tx_power']}")
        commands.append(f"meshtastic --port {port} --set lora.hop_limit {config['hop_limit']}")
        commands.append("")
        commands.append("# Device Role")
        commands.append(f"meshtastic --port {port} --set device.role {config['device_role']}")
        commands.append("")
        commands.append("# Telemetry (DHT22)")
        commands.append(f"meshtastic --port {port} --set telemetry.environment_measurement_enabled {'true' if config['telemetry_enabled'] else 'false'}")
        commands.append(f"meshtastic --port {port} --set telemetry.environment_update_interval {config['telemetry_interval']}")
        commands.append("")
        commands.append("# Bluetooth")
        commands.append(f"meshtastic --port {port} --set bluetooth.enabled {'true' if config['bluetooth_enabled'] else 'false'}")

        if config["wifi_enabled"]:
            commands.append("")
            commands.append("# WiFi Configuration")
            commands.append(f"meshtastic --port {port} --set network.wifi_enabled true")
            if config["wifi_ssid"]:
                commands.append(f'meshtastic --port {port} --set network.wifi_ssid "{config["wifi_ssid"]}"')
            if config["wifi_password"]:
                commands.append(f'meshtastic --port {port} --set network.wifi_psk "{config["wifi_password"]}"')

        commands.append("")
        commands.append("# Reboot to apply changes")
        commands.append(f"meshtastic --port {port} --reboot")

        return "\n".join(commands)

    def generate_commands(self):
        """Show generated CLI commands in a popup"""
        commands = self.generate_cli_commands()

        popup = tk.Toplevel(self.root)
        popup.title("Generated CLI Commands")
        popup.geometry("700x500")

        text = tk.Text(popup, wrap="word", font=("Courier", 10))
        text.pack(fill="both", expand=True, padx=10, pady=10)
        text.insert("1.0", commands)
        text.configure(state="disabled")

        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(commands)
            messagebox.showinfo("Copied", "Commands copied to clipboard!")

        ttk.Button(popup, text="Copy to Clipboard", command=copy_to_clipboard).pack(pady=10)

    def export_commands(self):
        """Export CLI commands to a file"""
        commands = self.generate_cli_commands()

        filepath = filedialog.asksaveasfilename(
            title="Export Commands",
            defaultextension=".sh",
            filetypes=[("Shell script", "*.sh"), ("Batch file", "*.bat"), ("Text file", "*.txt")],
            initialdir=os.path.dirname(self.config_file)
        )
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    f.write(commands)
                self.status_var.set(f"Commands exported to {filepath}")
                messagebox.showinfo("Exported", f"Commands saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")

    def apply_config(self):
        """Apply configuration to connected device"""
        if not messagebox.askyesno("Apply Configuration",
                                   "This will apply the configuration to the connected device.\n\n"
                                   "Make sure the device is connected and the correct COM port is selected.\n\n"
                                   "Continue?"):
            return

        config = self.get_current_config()
        port = self.port_var.get()

        commands = [
            ["meshtastic", "--port", port, "--set-owner", config["device_name"]],
            ["meshtastic", "--port", port, "--set-owner-short", config["short_name"]],
            ["meshtastic", "--port", port, "--set", "lora.region", config["region"]],
            ["meshtastic", "--port", port, "--set", "lora.modem_preset", config["modem_preset"]],
            ["meshtastic", "--port", port, "--set", "lora.tx_power", str(config["tx_power"])],
            ["meshtastic", "--port", port, "--set", "lora.hop_limit", str(config["hop_limit"])],
            ["meshtastic", "--port", port, "--set", "device.role", config["device_role"]],
            ["meshtastic", "--port", port, "--set", "telemetry.environment_measurement_enabled",
             "true" if config["telemetry_enabled"] else "false"],
            ["meshtastic", "--port", port, "--set", "telemetry.environment_update_interval",
             str(config["telemetry_interval"])],
            ["meshtastic", "--port", port, "--set", "bluetooth.enabled",
             "true" if config["bluetooth_enabled"] else "false"],
        ]

        if config["wifi_enabled"]:
            commands.append(["meshtastic", "--port", port, "--set", "network.wifi_enabled", "true"])
            if config["wifi_ssid"]:
                commands.append(["meshtastic", "--port", port, "--set", "network.wifi_ssid", config["wifi_ssid"]])
            if config["wifi_password"]:
                commands.append(["meshtastic", "--port", port, "--set", "network.wifi_psk", config["wifi_password"]])

        # Execute commands
        success_count = 0
        total = len(commands)

        progress = tk.Toplevel(self.root)
        progress.title("Applying Configuration")
        progress.geometry("400x150")
        progress.transient(self.root)

        ttk.Label(progress, text="Applying configuration...").pack(pady=10)
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress, variable=progress_var, maximum=total)
        progress_bar.pack(fill="x", padx=20, pady=10)
        status_label = ttk.Label(progress, text="")
        status_label.pack(pady=5)

        errors = []

        for i, cmd in enumerate(commands):
            status_label.configure(text=f"Running: {' '.join(cmd[:4])}...")
            progress.update()

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    success_count += 1
                else:
                    errors.append(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
            except Exception as e:
                errors.append(f"Error running: {' '.join(cmd)}\n{str(e)}")

            progress_var.set(i + 1)
            progress.update()

        progress.destroy()

        if success_count == total:
            if messagebox.askyesno("Success",
                                   f"All {total} settings applied successfully!\n\n"
                                   "Reboot device to apply changes?"):
                try:
                    subprocess.run(["meshtastic", "--port", port, "--reboot"],
                                  capture_output=True, timeout=30)
                    self.status_var.set("Configuration applied and device rebooted")
                except Exception as e:
                    messagebox.showwarning("Reboot Failed", f"Failed to reboot: {str(e)}")
        else:
            error_msg = f"Applied {success_count}/{total} settings.\n\nErrors:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                error_msg += f"\n... and {len(errors) - 5} more errors"
            messagebox.showwarning("Partial Success", error_msg)
            self.status_var.set(f"Applied {success_count}/{total} settings")

    def save_preinstall_config(self):
        """Save configuration as a pre-install config file (JSON format)"""
        config = self.get_current_config()

        # Create a structured config that can be used for fresh device setup
        preinstall_config = {
            "config_version": "1.0",
            "description": "Meshtastic Pre-Install Configuration",
            "device_name": config["device_name"],
            "short_name": config["short_name"],
            "lora": {
                "region": config["region"],
                "modem_preset": config["modem_preset"],
                "tx_power": config["tx_power"],
                "hop_limit": config["hop_limit"]
            },
            "device": {
                "role": config["device_role"]
            },
            "telemetry": {
                "environment_measurement_enabled": config["telemetry_enabled"],
                "environment_update_interval": config["telemetry_interval"]
            },
            "bluetooth": {
                "enabled": config["bluetooth_enabled"]
            },
            "network": {
                "wifi_enabled": config["wifi_enabled"],
                "wifi_ssid": config["wifi_ssid"] if config["wifi_enabled"] else "",
                "wifi_password": config["wifi_password"] if config["wifi_enabled"] else ""
            }
        }

        # Ask user where to save
        filepath = filedialog.asksaveasfilename(
            title="Save Pre-Install Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.path.dirname(self.config_file),
            initialfile="meshtastic_preinstall_config.json"
        )

        if filepath:
            try:
                with open(filepath, 'w') as f:
                    json.dump(preinstall_config, f, indent=2)
                self.status_var.set(f"Pre-install config saved to {filepath}")
                messagebox.showinfo("Success",
                                   f"Pre-install configuration saved!\n\n"
                                   f"File: {filepath}\n\n"
                                   f"You can load this configuration on any fresh device using:\n"
                                   f"1. 'Load Config' button in this GUI\n"
                                   f"2. The generated setup script\n"
                                   f"3. Manual CLI commands")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save pre-install config: {str(e)}")

    def export_setup_script(self):
        """Export a complete setup script for fresh device configuration"""
        config = self.get_current_config()

        # Create a comprehensive setup script
        script_content = f"""#!/bin/bash
# Meshtastic Device Setup Script
# Generated by Meshtastic DHT22 Configuration GUI
#
# This script configures a freshly flashed Meshtastic device with your settings.
#
# Usage:
#   Windows (Git Bash/WSL): bash setup_device.sh COM3
#   Linux/Mac: ./setup_device.sh /dev/ttyUSB0
#
# Make executable on Linux/Mac: chmod +x setup_device.sh

set -e  # Exit on error

# Check if port argument provided
if [ -z "$1" ]; then
    echo "ERROR: No port specified!"
    echo "Usage: $0 <port>"
    echo "Example (Windows): $0 COM3"
    echo "Example (Linux): $0 /dev/ttyUSB0"
    exit 1
fi

PORT="$1"
echo "========================================="
echo "Meshtastic Device Configuration Script"
echo "========================================="
echo "Port: $PORT"
echo "Device: {config['device_name']}"
echo ""

# Check if meshtastic CLI is installed
if ! command -v meshtastic &> /dev/null; then
    echo "ERROR: meshtastic CLI not found!"
    echo "Install with: pip install meshtastic"
    exit 1
fi

# Test connection
echo "Testing connection to device..."
if ! meshtastic --port "$PORT" --info &> /dev/null; then
    echo "ERROR: Cannot connect to device on $PORT"
    echo "Make sure:"
    echo "  1. Device is connected via USB"
    echo "  2. Correct port is specified"
    echo "  3. Device is not already in use"
    exit 1
fi
echo "Connection successful!"
echo ""

# Apply configuration
echo "Applying configuration..."
echo ""

echo "[1/11] Setting device name..."
meshtastic --port "$PORT" --set-owner "{config['device_name']}"

echo "[2/11] Setting short name..."
meshtastic --port "$PORT" --set-owner-short "{config['short_name']}"

echo "[3/11] Setting LoRa region..."
meshtastic --port "$PORT" --set lora.region {config['region']}

echo "[4/11] Setting modem preset..."
meshtastic --port "$PORT" --set lora.modem_preset {config['modem_preset']}

echo "[5/11] Setting TX power..."
meshtastic --port "$PORT" --set lora.tx_power {config['tx_power']}

echo "[6/11] Setting hop limit..."
meshtastic --port "$PORT" --set lora.hop_limit {config['hop_limit']}

echo "[7/11] Setting device role..."
meshtastic --port "$PORT" --set device.role {config['device_role']}

echo "[8/11] Configuring telemetry..."
meshtastic --port "$PORT" --set telemetry.environment_measurement_enabled {'true' if config['telemetry_enabled'] else 'false'}
meshtastic --port "$PORT" --set telemetry.environment_update_interval {config['telemetry_interval']}

echo "[9/11] Configuring Bluetooth..."
meshtastic --port "$PORT" --set bluetooth.enabled {'true' if config['bluetooth_enabled'] else 'false'}

echo "[10/11] Configuring WiFi..."
"""

        if config["wifi_enabled"]:
            script_content += f"""meshtastic --port "$PORT" --set network.wifi_enabled true
meshtastic --port "$PORT" --set network.wifi_ssid "{config['wifi_ssid']}"
meshtastic --port "$PORT" --set network.wifi_psk "{config['wifi_password']}"
"""
        else:
            script_content += """# WiFi disabled
meshtastic --port "$PORT" --set network.wifi_enabled false
"""

        script_content += f"""
echo "[11/11] Rebooting device..."
meshtastic --port "$PORT" --reboot

echo ""
echo "========================================="
echo "Configuration Complete!"
echo "========================================="
echo "Device will reboot and apply settings."
echo ""
echo "Configuration Summary:"
echo "  Name: {config['device_name']}"
echo "  Short: {config['short_name']}"
echo "  Region: {config['region']}"
echo "  Modem: {config['modem_preset']}"
echo "  Role: {config['device_role']}"
echo "  TX Power: {config['tx_power']} dBm"
echo "  Bluetooth: {'Enabled' if config['bluetooth_enabled'] else 'Disabled'}"
echo "  WiFi: {'Enabled' if config['wifi_enabled'] else 'Disabled'}"
echo ""
echo "Wait 10-15 seconds for device to restart."
echo "Then check with: meshtastic --port $PORT --info"
"""

        # Also create a Windows batch file version
        batch_content = f"""@echo off
REM Meshtastic Device Setup Script (Windows)
REM Generated by Meshtastic DHT22 Configuration GUI

if "%1"=="" (
    echo ERROR: No port specified!
    echo Usage: %0 ^<port^>
    echo Example: %0 COM3
    exit /b 1
)

set PORT=%1
echo =========================================
echo Meshtastic Device Configuration Script
echo =========================================
echo Port: %PORT%
echo Device: {config['device_name']}
echo.

echo Testing connection to device...
meshtastic --port %PORT% --info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Cannot connect to device on %PORT%
    echo Make sure:
    echo   1. Device is connected via USB
    echo   2. Correct port is specified
    echo   3. Device is not already in use
    exit /b 1
)
echo Connection successful!
echo.

echo Applying configuration...
echo.

echo [1/11] Setting device name...
meshtastic --port %PORT% --set-owner "{config['device_name']}"

echo [2/11] Setting short name...
meshtastic --port %PORT% --set-owner-short "{config['short_name']}"

echo [3/11] Setting LoRa region...
meshtastic --port %PORT% --set lora.region {config['region']}

echo [4/11] Setting modem preset...
meshtastic --port %PORT% --set lora.modem_preset {config['modem_preset']}

echo [5/11] Setting TX power...
meshtastic --port %PORT% --set lora.tx_power {config['tx_power']}

echo [6/11] Setting hop limit...
meshtastic --port %PORT% --set lora.hop_limit {config['hop_limit']}

echo [7/11] Setting device role...
meshtastic --port %PORT% --set device.role {config['device_role']}

echo [8/11] Configuring telemetry...
meshtastic --port %PORT% --set telemetry.environment_measurement_enabled {'true' if config['telemetry_enabled'] else 'false'}
meshtastic --port %PORT% --set telemetry.environment_update_interval {config['telemetry_interval']}

echo [9/11] Configuring Bluetooth...
meshtastic --port %PORT% --set bluetooth.enabled {'true' if config['bluetooth_enabled'] else 'false'}

echo [10/11] Configuring WiFi...
"""

        if config["wifi_enabled"]:
            batch_content += f"""meshtastic --port %PORT% --set network.wifi_enabled true
meshtastic --port %PORT% --set network.wifi_ssid "{config['wifi_ssid']}"
meshtastic --port %PORT% --set network.wifi_psk "{config['wifi_password']}"
"""
        else:
            batch_content += """REM WiFi disabled
meshtastic --port %PORT% --set network.wifi_enabled false
"""

        batch_content += f"""
echo [11/11] Rebooting device...
meshtastic --port %PORT% --reboot

echo.
echo =========================================
echo Configuration Complete!
echo =========================================
echo Device will reboot and apply settings.
echo.
echo Configuration Summary:
echo   Name: {config['device_name']}
echo   Short: {config['short_name']}
echo   Region: {config['region']}
echo   Modem: {config['modem_preset']}
echo   Role: {config['device_role']}
echo   TX Power: {config['tx_power']} dBm
echo   Bluetooth: {'Enabled' if config['bluetooth_enabled'] else 'Disabled'}
echo   WiFi: {'Enabled' if config['wifi_enabled'] else 'Disabled'}
echo.
echo Wait 10-15 seconds for device to restart.
echo Then check with: meshtastic --port %PORT% --info
pause
"""

        # Ask user where to save (offer both .sh and .bat)
        filepath = filedialog.asksaveasfilename(
            title="Export Setup Script",
            defaultextension=".sh",
            filetypes=[
                ("Bash script", "*.sh"),
                ("Windows batch file", "*.bat"),
                ("All files", "*.*")
            ],
            initialdir=os.path.dirname(self.config_file),
            initialfile="setup_meshtastic_device.sh"
        )

        if filepath:
            try:
                # Determine which content to save based on extension
                if filepath.endswith('.bat'):
                    content = batch_content
                else:
                    content = script_content

                with open(filepath, 'w', newline='\n') as f:
                    f.write(content)

                # Make executable on Unix-like systems
                if not filepath.endswith('.bat'):
                    try:
                        os.chmod(filepath, 0o755)
                    except Exception:
                        pass  # Windows doesn't support chmod

                # Also save the companion file (.sh <-> .bat)
                companion_path = None
                if filepath.endswith('.sh'):
                    companion_path = filepath[:-3] + '.bat'
                    companion_content = batch_content
                elif filepath.endswith('.bat'):
                    companion_path = filepath[:-4] + '.sh'
                    companion_content = script_content

                if companion_path:
                    try:
                        with open(companion_path, 'w', newline='\n') as f:
                            f.write(companion_content)
                        if companion_path.endswith('.sh'):
                            try:
                                os.chmod(companion_path, 0o755)
                            except Exception:
                                pass
                    except Exception:
                        pass  # Companion file is optional

                self.status_var.set(f"Setup script exported to {filepath}")
                messagebox.showinfo("Success",
                                   f"Setup script exported!\n\n"
                                   f"Main file: {os.path.basename(filepath)}\n"
                                   + (f"Companion: {os.path.basename(companion_path)}\n" if companion_path else "") +
                                   f"\nUsage:\n"
                                   f"  Windows: {os.path.basename(filepath)} COM3\n"
                                   f"  Linux/Mac: ./{os.path.basename(filepath)} /dev/ttyUSB0\n\n"
                                   f"This script will configure any freshly flashed device\n"
                                   f"with your current settings.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export setup script: {str(e)}")


def main():
    root = tk.Tk()

    # Try to set a modern theme
    try:
        style = ttk.Style()
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'vista' in available_themes:
            style.theme_use('vista')
    except Exception:
        pass

    app = MeshtasticConfigGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
