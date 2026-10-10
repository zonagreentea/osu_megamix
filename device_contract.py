
"""Device Contract compatibility wrapper for KNU.

KNU supplies communication.
This wrapper enforces the application's device-session policy.

The KNU adapter passed to this class must expose:
    connect(device)
    disconnect(session)
    send(session, message)
    read(session)

These adapter signatures are an interface expectation, not a claim
about the exact current KNU.zsh implementation.
"""


class DeviceContractError(Exception):
    """A device operation violates the contract."""


class DeviceContract:
    """Validate device operations before delegating them to KNU."""

    def __init__(self, knu, allowed_capabilities=()):
        self.knu = knu
        self.allowed_capabilities = frozenset(allowed_capabilities)
        self.sessions = {}

    def connect(self, device, capabilities=()):
        """Connect a device with explicitly permitted capabilities."""
        capabilities = frozenset(capabilities)

        if not device:
            raise DeviceContractError("A device identifier is required.")

        if device in self.sessions:
            raise DeviceContractError("Device is already connected.")

        if not capabilities.issubset(self.allowed_capabilities):
            raise DeviceContractError("Requested capability is not permitted.")

        session = self.knu.connect(device)

        if session is None:
            raise DeviceContractError("KNU did not establish a session.")

        self.sessions[device] = {
            "session": session,
            "capabilities": capabilities,
        }
        return session

    def disconnect(self, device):
        """Disconnect a device and revoke its contract session."""
        record = self.sessions.get(device)
        if record is None:
            return False

        # Revoke local authorization even if transport teardown fails.
        del self.sessions[device]
        self.knu.disconnect(record["session"])
        return True

    def send(self, device, message, capability):
        """Send a message only through an authorized active session."""
        record = self.sessions.get(device)
        if record is None:
            raise DeviceContractError("Device is not connected.")

        if capability not in record["capabilities"]:
            raise DeviceContractError("Capability is not authorized.")

        if message is None:
            raise DeviceContractError("Message cannot be None.")

        return self.knu.send(record["session"], message)

    def read(self, device, capability):
        """Read only through an authorized active session."""
        record = self.sessions.get(device)
        if record is None:
            raise DeviceContractError("Device is not connected.")

        if capability not in record["capabilities"]:
            raise DeviceContractError("Capability is not authorized.")

        return self.knu.read(record["session"])
