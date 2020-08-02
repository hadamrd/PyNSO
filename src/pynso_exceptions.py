class NoSPRegistrationError(Exception):
    pass

class OutOfSyncError(Exception):
    pass

class NsoCmdAbortedError(Exception):
    pass

class NoNetsimDirectoryFoundError(Exception):
    pass

class StillInZombieStateError(Exception):
    pass
