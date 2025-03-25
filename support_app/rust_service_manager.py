import psutil
import pywintypes
import win32service
import win32serviceutil


class ServiceManager:
    def __init__(self, service_name, display_name, binary_path):
        self.service_name = service_name
        self.display_name = display_name
        self.binary_path = binary_path

    def is_service_installed(self):
        try:
            win32serviceutil.QueryServiceStatus(self.service_name)
            return True
        except Exception as e:
            if isinstance(e, pywintypes.error) and e.winerror == 1060:
                print(f"Service {self.service_name} does not exist.")
            return False

    def create_service(self):
        if not self.is_service_installed():
            try:
                # Open a handle to the service control manager
                scm_handle = win32service.OpenSCManager(
                    None, None, win32service.SC_MANAGER_CREATE_SERVICE
                )

                # Create the service
                service_handle = win32service.CreateService(
                    scm_handle,
                    self.service_name,
                    self.display_name,
                    win32service.SERVICE_ALL_ACCESS,
                    win32service.SERVICE_WIN32_OWN_PROCESS,
                    win32service.SERVICE_DEMAND_START,
                    win32service.SERVICE_ERROR_NORMAL,
                    self.binary_path,
                    None,
                    0,
                    None,
                    None,
                    None,
                )

                # Close the handles
                win32service.CloseServiceHandle(service_handle)
                win32service.CloseServiceHandle(scm_handle)

                print(f"Service {self.service_name} created successfully.")
            except Exception as e:
                print(f"Failed to create service: {e}")

    def delete_service(self):
        if self.is_service_installed():
            try:
                win32serviceutil.RemoveService(self.service_name)
                print(f"Service {self.service_name} deleted successfully.")
            except Exception as e:
                print(f"Failed to delete service: {e}")

    def start_service(self):
        try:
            win32serviceutil.StartService(self.service_name)
            print(f"Service {self.service_name} started successfully.")
        except Exception as e:
            if isinstance(e, pywintypes.error):
                if e.winerror == 1056:
                    print(f"Service {self.service_name} is already running.")
                elif e.winerror == 1060:
                    print(f"Service {self.service_name} does not exist.")
                else:
                    print(f"Failed to start service: {e}")

    def stop_service(self):
        try:
            win32serviceutil.StopService(self.service_name)
            print(f"Service {self.service_name} stopped successfully.")
        except Exception as e:
            if isinstance(e, pywintypes.error):
                if e.winerror == 1062:
                    print(f"Service {self.service_name} is not running.")
                elif e.winerror == 1060:
                    print(f"Service {self.service_name} does not exist.")
                else:
                    print(f"Failed to stop service: {e}")
