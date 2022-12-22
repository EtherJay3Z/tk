from os import path

from Configuration import Settings
from DataAcquirer import UserData
from DataDownloader import Download
from Recorder import DataLogger
from Recorder import RunLogger

CLEAN_PATCH = {
    " ": " ",
}


class  TikTok :
    def __init__(self):
        self.record = None
        self.request = None
        self.download = None
        self.settings = Settings()
        self . accounts  = []   # account data
        self . __number  =  0   # Number of accounts
        self .__data  = {}   # other configuration data

    def check_config(self):
        settings = self.settings.read()
        try:
            return self.read_data(settings)
        except KeyError as e:
            self . record . error ( f"Error reading configuration file: { e } " )
            select = input(
                "An exception occurred while reading the configuration file! Do you need to regenerate the default configuration file? (Y/N)" )
            if select == "Y":
                self.settings.create()
            print ( "The program is about to close, please check the configuration file and then run the program again!" )
            return  False

    def read_data(self, settings):
        self.accounts = settings["accounts"]
        self.__number = len(self.accounts)
        self.__data["root"] = settings["root"]
        self.__data["folder"] = settings["folder"]
        self.__data["name"] = settings["name"]
        self.__data["music"] = settings["music"]
        self.__data["time"] = settings["time"]
        self.__data["split"] = settings["split"]
        self.__data["save"] = settings["save"]
        self . record . info ( "read configuration file successfully" )
        return True

    def batch_acquisition(self):
        self.set_parameters()
        self . record . info ( f"A total of { self . __number } account works are waiting to be downloaded" )
        for  index  in  range ( self . __number ):
            self.account_download(index + 1, *self.accounts[index])

    def account_download(self, num: int, url: str, mode: str):
        self.request.url = url
        self.request.api = mode
        type_  = { "post" : "post page" , "like" : "like page" }[ mode ]
        if not self.request.run(num):
            return  False
        self . record . info ( f"Account { self . request . name } starts batch downloading { type_ } works!" )
        self.download.nickname = self.request.name
        with DataLogger(self.__data["save"], name=self.download.nickname) as data:
            self.data_settings(data)
            self.download.run(
                self.request.video_data,
                self.request.image_data)
        self . record . info ( f"Account { self . request . name } batch download { type_ } work is over!" )
        self.download._nickname = None
        return True

    def single_acquisition(self):
        self.set_parameters()
        with DataLogger(self.__data["save"]) as data:
            self.data_settings(data)
            while True:
                url  =  input ( "Please enter the share link: " )
                if url in ("Q", "q", ""):
                    break
                id_ = self.request.run_alone(url)
                if  not  id_ :
                    self . record . error ( f" { url } failed to get item_ids!" )
                    continue
                self.download.run_alone(id_)

    def data_settings(self, file):
        self.download.data = file
        if path.getsize(file.root) == 0:
            # If the file doesn't have any data, write the header line
            self.download.data.save(
                [ "Type" , "Work ID" , "Description" , "Creation Time" , "Account Nickname" , "video_id" , ])

    def initialize(self, **kwargs):
        self.record = RunLogger()
        self.record.root = kwargs["root"]
        self.record.name = kwargs["name"]
        self.record.run()
        self.request = UserData(self.record)
        self.download = Download(self.record, None)
        self.download.clean.set_rule(CLEAN_PATCH, True)

    def set_parameters(self):
        self.download.root = self.__data["root"]
        self.download.folder = self.__data["folder"]
        self.download.name = self.__data["name"]
        self.download.music = self.__data["music"]
        self.download.time = self.__data["time"]
        self.download.split = self.__data["split"]

    def run(self, root="./", name="%Y-%m-%d %H.%M.%S"):
        self.initialize(root=root, name=name)
        self . record . info ( "The program starts running" )
        if not self.check_config():
            return  False
        select  =  input ( "Please select the download mode: \n 1. Batch download user works source \n 2. Download linked works individually \nEnter serial number:" )
        match select:
            case "1":
                self . record . info ( "The batch download mode has been selected" )
                self.batch_acquisition()
            case "2":
                self . record . info ( "The mode of downloading works individually has been selected" )
                self.single_acquisition()
            case "Q" | "q" | "":
                pass
            case _:
                self . record . warning ( f"Invalid input when selecting download mode: " { select } "" )
        self . record . info ( "The program is finished" )


def main():
    example  =  TikTok ()
    example.run()


if __name__ == '__main__':
    main()
