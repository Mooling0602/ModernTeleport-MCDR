from mcdreforged.api.all import Serializable


class RconSettings(Serializable):
    fallback_mcdr: bool = True
    force_enable: bool = False


class FeatureOptions(Serializable):
    back: bool = True
    home: bool = True
    tpm: bool = True
    warp: bool = True
    waypoint: bool = True
    cost: bool = False


class MTPConfig(Serializable):
    rcon: RconSettings = RconSettings()
    features: FeatureOptions = FeatureOptions()
