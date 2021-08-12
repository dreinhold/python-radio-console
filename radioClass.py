from enum import Enum
import json

class RadioState(Enum):
    """Radio status enum
    """
    # Standard connection states
    Disconnected = 0
    Idle = 0
    Receiving = 1
    Transmitting = 2
    # Error states
    ConnectError = 10
    TransmitError = 11
    ReceiveError = 12
    UnknownError = 20

class Radio():
    """Radio Class for generic radio control
    """
    
    # Valid control modes for the radio
    controlModes = ["None",             # No PTT control
                    "SB9600-XTL-O",     # XTL O-head
                    "SB9600-XTL-W",     # XTL W-head
                    "SB9600-SPECTRA",   # Astro Spectra W-head
                    "SB9600-MCS",       # MCS2000
                    "Soundcard-CM108",  # CM108 GPIO PTT
                    "Soundcard-VOX"]    # Radio-controlled VOX PTT

    # Valid signalling modes for the radio
    signallingModes = ["None",
                       "MDC",
                       "ANI",
                       "Singletone",
                       "QCII"]

    # Init class
    def __init__(self, name, desc=None, ctrlMode=None, ctrlPort=None, txDev=None, rxDev=None, signalMode=None, signalId=None):
        """Radio configuration object

        Args:
            name (string): Radio name
            desc (string): Radio description
            ctrlMode (string): Radio control mode (SB9600, CAT, etc)
            ctrlDev (string): Device for radio control (serial, USB, IP, etc)
            txDev (string): Transmit audio device
            rxDev (string): Receieve audio device
            signalMode (string): Optional signalling mode
            signalId (any): Optional signalling ID
        """

        # Save parameters
        self.name = name
        self.desc = desc
        self.ctrlMode = ctrlMode
        self.ctrlPort = ctrlPort
        self.txDev = txDev
        self.rxDev = rxDev
        self.sigMode = signalMode
        self.sigId = signalId

        # Init client-facing parameters
        self.zone = ""
        self.chan = ""
        self.lastid = ""
        self.muted = False
        self.error = False
        self.scanning = False
        self.talkaround = False
        self.monitor = False
        self.lowpower = False

        # Set starting status to disconnected
        self.state = RadioState.Disconnected

    def getState(self):
        """Return current state of radio

        Returns:
            RadioState: current status of radio
            StateString: string representation of current status
        """

        if self.state.value < 10:
            stateString = self.state.name
            self.error = False
        else:
            self.error = True
            if self.state == RadioState.ConnectError:
                stateString = "Connection Error"
            elif self.state == RadioState.TransmitError:
                stateString = "Transmit Error"
            elif self.state == RadioState.ReceiveError:
                stateString = "Receive Error"
            else:
                stateString = "Unknown Error"

        return self.state, stateString

    def encodeClientStatus(self):
        """Encode radio status into a dict for sending to the client

        Returns:
            dict: Dict of radio status variables
        """
        # Get overall radio status
        state, stateString = self.getState()

        # Send error text if there's an error, or state text otherwise
        if state.value >= 10:
            stateText = "Error"
            errorText = stateString
        else:
            stateText = stateString
            errorText = ""

        # Encode status variables into a dict
        clientStatus = {
            "name": self.name,
            "zone": self.zone,
            "chan": self.chan,
            "lastid": self.lastid,
            "state": stateText,
            "muted": self.muted,
            "error": self.error,
            "errorText": errorText,
            "scanning": self.scanning,
            "talkaround": self.talkaround,
            "monitor": self.monitor,
            "lowpower": self.lowpower
        }
        
        # Return the dict
        return clientStatus

    def encodeConfig(self):
        """Encode radio parameters into config dict for JSON parsing

        Returns:
            dict: radio config parameters in dict form
        """
        # Create dict
        config = {
            "name": self.name,
            "desc": self.desc,
            "ctrlMode": self.ctrlMode,
            "ctrlPort": self.ctrlPort,
            "txDevice": self.txDev,
            "rxDevice": self.rxDev,
            "sigMode": self.sigMode,
            "sigId": self.sigId
        }
        return config

    def decodeConfig(radioDict):
        """Decode a dict of config parameters into a new radio object

        Args:
            radioDict (dict): Dict of radio parameters

        Returns:
            Radio: a new Radio object
        """
        # create a new radio object from config data
        return Radio(radioDict['name'],
                     radioDict['desc'],
                     radioDict['ctrlMode'],
                     radioDict['ctrlPort'],
                     radioDict['txDevice'],
                     radioDict['rxDevice'],
                     radioDict['sigMode'],
                     radioDict['sigId'])