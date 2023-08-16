import gi
import os
import sys
import uuid
import stat
import signal
import atexit
import subprocess
 
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

# Global variables for authentication and IP type
authentication = ""
ip_type = ""

class APNConfiguratorWindow(Gtk.Window):

    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("apnsetting_display.glade")
        builder.connect_signals(self)

        window = builder.get_object("window-obj")
        window.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(0.7, 0.7, 0.7, 0.7))
        window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        window.set_resizable(False)
        window.resize(700,550)
        window.set_title("APN Configurator")

        screen = window.get_screen()
        visual = screen.get_rgba_visual()
        window.set_visual(visual)

        #set window objects
        self.txtBox_profile_name = builder.get_object("txtBox-profile-name")
        self.txtBox_apn = builder.get_object("txtBox-apn")
        self.txtBox_username = builder.get_object("txtBox-username")
        self.txtBox_password = builder.get_object("txtBox-password")
        self.chkBox_ipv4 = builder.get_object("chkBox-ipv4")
        self.chkBox_ipv6 = builder.get_object("chkBox-ipv6")
        self.chkBox_pap = builder.get_object("chkBox-pap")
        self.chkBox_chap = builder.get_object("chkBox-chap")
        self.txtView_logs = builder.get_object("txtView-logs")
        self.buf_txtViewLogs_buffer = builder.get_object("buf-txtViewLogs-buffer")
        self.txtBox_profile_name = builder.get_object("txtBox-profile-name")
        self.txtBox_username = builder.get_object("txtBox-username")
        self.txtBox_password = builder.get_object("txtBox-password")
        self.txtBox_apn = builder.get_object("txtBox-apn")
        self.listBox_prof_apn = builder.get_object("listBox-prof-apn")
        self.listBox_user_pw = builder.get_object("listBox-user-pw")

        self.provider = Gtk.CssProvider()
        self.provider.load_from_path("lib/css/custom.css")

        self.listBox_prof_apn_style = self.listBox_prof_apn.get_style_context()
        self.listBox_user_pw_style = self.listBox_user_pw.get_style_context()
        self.txtBox_profile_name_style = self.txtBox_profile_name.get_style_context()
        self.txtBox_apn_style = self.txtBox_apn.get_style_context()
        self.txtBox_username_style = self.txtBox_username.get_style_context()
        self.txtBox_password_style = self.txtBox_password.get_style_context()
        self.txtView_logs_style = self.txtView_logs.get_style_context()
        self.listBox_prof_apn_style.add_provider(self.provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.listBox_user_pw_style.add_provider(self.provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.txtBox_profile_name_style.add_provider(self.provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.txtBox_apn_style.add_provider(self.provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.txtBox_username_style.add_provider(self.provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.txtBox_password_style.add_provider(self.provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.txtView_logs_style.add_provider(self.provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)         

        self.buf_txtViewLogs_buffer.set_text("Please Enter your APN details in the text box" + '\n')
        self.txtView_logs.set_buffer(self.buf_txtViewLogs_buffer)

        window.connect("destroy", Gtk.main_quit)
        window.show_all() 

    def switch_on_mobile_broadband(self):
        subprocess.run(["nmcli", "radio", "wwan", "on"])

    def refresh_network_manager_settings(self):
        subprocess.run(["nmcli", "connection", "reload"])

    def restart_network_manager(self):
        subprocess.run(["sudo", "systemctl", "restart", "NetworkManager"])

    # Function to create or modify the mobile broadband profile
    def create_or_modify_mobile_broadband_profile_nm(self, profile_name, apn, ip_type, username, password, authentication):

        new_uuid = str(uuid.uuid4()) # generating new UUID

        # Create a new connection profile file
        connection_file_path = f"/etc/NetworkManager/system-connections/{profile_name}"
        with open(connection_file_path, 'w') as connection_file:
            connection_file.write("[connection]\n")
            connection_file.write("id=" + profile_name + "\n")
            connection_file.write("uuid=" + new_uuid + "\n")  # Set the generated UUID
            connection_file.write("type=gsm\n")
    #       connection_file.write("autoconnect=true\n")
            connection_file.write("\n")
            connection_file.write("[gsm]\n")
            connection_file.write("apn=" + apn + "\n")
            if username:
                connection_file.write("username=" + username + "\n")
            if password:
                connection_file.write("password=" + password + "\n")
            connection_file.write("ip-type=" + ip_type + "\n")
            connection_file.write("allowed-auth=" + authentication + "\n")

        # Set the correct permissions on the connection file
        os.chmod(connection_file_path, stat.S_IRUSR | stat.S_IWUSR)

        # Refresh Network Manager settings
        self.refresh_network_manager_settings()
        print("Network Manager settings refreshed.")

        self.restart_network_manager()
        print("Network Manager restarted.")

        # Switch on the mobile broadband connection
        self.switch_on_mobile_broadband()
        print("Mobile broadband is switched on.")

    def chkBox_ipv6_toggled(self, button):
        global ip_type
        if self.chkBox_ipv4.get_active():
            ip_type = "IPV4V6"
        else:
            ip_type = "IPV6"                                                                                                                                                                                                                                                                                                                                           

    def chkBox_ipv4_toggled(self, button):
        global ip_type
        if self.chkBox_ipv6.get_active():
            ip_type = "IPV4V6"
        else:
            ip_type = "IPV4"
    
    def chkBox_pap_toggled(self, button):
        global authentication
        if self.chkBox_chap.get_active():
            authentication = "PAP/CHAP"
        else:
            authentication = "PAP"
    
    def chkBox_chap_toggled(self, button):
        global authentication
        if self.chkBox_pap.get_active():
            authentication = "PAP/CHAP"
        else:
            if authentication:
                authentication += "/"
            authentication += "CHAP"

    def btn_connect_clicked(self, button):
        self.send_at_command()

    def btn_exit_clicked(self, button):
        exithandle.exit_handle()

    def modify_mobile_broadband_profile(self, profile_name, apn, ip_type, username, password, authentication):

        subprocess.run(["nmcli", "c", "modify", profile_name, "gsm.apn", apn])
        subprocess.run(["nmcli", "c", "modify", profile_name, "gsm.username", username])
        subprocess.run(["nmcli", "c", "modify", profile_name, "gsm.password", password])

        iter = self.buf_txtViewLogs_buffer.get_end_iter()
        self.buf_txtViewLogs_buffer.insert(iter, "Mobile broadband profile created successfully." + '\n')
        self.txtView_logs.set_buffer(self.buf_txtViewLogs_buffer)

        # Configure authentication options based on the selected method
        if authentication.lower() in ["pap"]:
            subprocess.run(["nmcli", "c", "modify", profile_name, "ppp.refuse-eap", "yes"])
            subprocess.run(["nmcli", "c", "modify", profile_name, "ppp.refuse-chap", "yes"])
            subprocess.run(["nmcli", "c", "modify", profile_name, "ppp.refuse-mschap", "yes"])
            subprocess.run(["nmcli", "c", "modify", profile_name, "ppp.refuse-mschapv2", "yes"])
        elif authentication.lower() in ["chap"]:
            subprocess.run(["nmcli", "c", "modify", profile_name, "ppp.refuse-eap", "yes"])
            subprocess.run(["nmcli", "c", "modify", profile_name, "ppp.refuse-pap", "yes"])
            subprocess.run(["nmcli", "c", "modify", profile_name, "ppp.refuse-mschap", "yes"])
            subprocess.run(["nmcli", "c", "modify", profile_name, "ppp.refuse-mschapv2", "yes"])
        elif authentication.lower() in ["pap/chap", "chap/pap"]:
            subprocess.run(["nmcli", "c", "modify", profile_name, "ppp.refuse-eap", "yes"])
            subprocess.run(["nmcli", "c", "modify", profile_name, "ppp.refuse-chap", "no"])
            subprocess.run(["nmcli", "c", "modify", profile_name, "ppp.refuse-pap", "no"])
            subprocess.run(["nmcli", "c", "modify", profile_name, "ppp.refuse-mschap", "yes"])
            subprocess.run(["nmcli", "c", "modify", profile_name, "ppp.refuse-mschapv2", "yes"])

        # Configure IP type options
        if ip_type.lower() == "ipv4":
            subprocess.run(["nmcli", "c", "modify", profile_name, "ipv4.method", "auto"])
            subprocess.run(["nmcli", "c", "modify", profile_name, "ipv6.method", "disabled"])
        elif ip_type.lower() == "ipv6":
            subprocess.run(["nmcli", "c", "modify", profile_name, "ipv4.method", "disabled"])
            subprocess.run(["nmcli", "c", "modify", profile_name, "ipv6.method", "auto"])
        elif ip_type.lower() == "ipv4v6":
            subprocess.run(["nmcli", "c", "modify", profile_name, "ipv4.method", "auto"])
            subprocess.run(["nmcli", "c", "modify", profile_name, "ipv6.method", "auto"])

    def mmcli_port_checker(self):
        mmcli_port_check = subprocess.check_output(['mmcli', '-L']).decode('utf-8')
        mmcli_port = mmcli_port_check.rfind("/")
        mmcli_port_number = mmcli_port_check[mmcli_port + 1:].strip()
        port = mmcli_port_number.split()                                    
        return port[0]	

    def send_at_command(self):
        global authentication, ip_type

        #filling variables from textbox
        profile_name = self.txtBox_profile_name.get_text()
        iter0 = self.buf_txtViewLogs_buffer.get_end_iter()
        self.buf_txtViewLogs_buffer.insert(iter0, "Profile Name:" + profile_name + '\n')
        self.txtView_logs.set_buffer(self.buf_txtViewLogs_buffer)

        #apn_name = apn_entry.get()
        apn_name = self.txtBox_apn.get_text()
        auth_type = authentication
        iter1 = self.buf_txtViewLogs_buffer.get_end_iter()
        self.buf_txtViewLogs_buffer.insert(iter1, "APN:" + apn_name + '\n')
        self.txtView_logs.set_buffer(self.buf_txtViewLogs_buffer)

        #user_name = user_entry.get()
        user_name = self.txtBox_username.get_text()
        iter2 = self.buf_txtViewLogs_buffer.get_end_iter()
        self.buf_txtViewLogs_buffer.insert(iter2, "Username:" + user_name + '\n')
        self.txtView_logs.set_buffer(self.buf_txtViewLogs_buffer)

        #password = pass_entry.get()
        password = self.txtBox_password.get_text()
        iter3 = self.buf_txtViewLogs_buffer.get_end_iter()
        self.buf_txtViewLogs_buffer.insert(iter3, "Password:" + password + '\n')
        self.txtView_logs.set_buffer(self.buf_txtViewLogs_buffer)

        #fixing the commands
        command = '--3gpp-set-initial-eps-bearer-settings=apn=' + apn_name + ',ip-type=' + ip_type + ',allowed-auth=' + auth_type + ',user=' + user_name + ',password=' + password

        #calling port checker function
        port_number = self.mmcli_port_checker()

        iter4 = self.buf_txtViewLogs_buffer.get_end_iter()
        self.buf_txtViewLogs_buffer.insert(iter4, "Port detected is " + port_number + '\n')
        self.txtView_logs.set_buffer(self.buf_txtViewLogs_buffer)

        result = subprocess.run(['mmcli', '-m', port_number, command], capture_output=True, text=True)

        iter5 = self.buf_txtViewLogs_buffer.get_end_iter()
        self.buf_txtViewLogs_buffer.insert(iter5, result.stdout)
        self.txtView_logs.set_buffer(self.buf_txtViewLogs_buffer)

        iter6 = self.buf_txtViewLogs_buffer.get_end_iter()
        self.buf_txtViewLogs_buffer.insert(iter6, result.stderr)
        self.txtView_logs.set_buffer(self.buf_txtViewLogs_buffer)

        #setting values for Network manager GUI
        self.create_or_modify_mobile_broadband_profile_nm(profile_name, apn_name, ip_type, user_name, password, auth_type)

        #setting values in Network manager nmcli method
        self.modify_mobile_broadband_profile(profile_name, apn_name, ip_type, user_name, password, auth_type)
        
class ExitHandler():
    def __init__(self):
        atexit.register(self.exit_handle)
        
        #Call exit_handle even if kill{pid} is used
        signal.signal(signal.SIGTERM, self.exit_handle)
        signal.signal(signal.SIGINT, self.exit_handle)

    def exit_handle(self):      
        print("\nExited APN Configurator")
        sys.exit(0)

if __name__ == "__main__":
    window = APNConfiguratorWindow()
    exithandle = ExitHandler()
    Gtk.main()


