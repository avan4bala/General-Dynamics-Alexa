from ask_sdk_core.skill_builder import SkillBuilder


class SingletonSkillBuilder(SkillBuilder):
    __instance = None

    def __new__(cls):
        if SingletonSkillBuilder.__instance is None:
            SingletonSkillBuilder.__instance = object.__new__(cls)
        return SingletonSkillBuilder.__instance


sb = SkillBuilder()


if __name__ == "__main__":
    print(SingletonSkillBuilder())
    print(SingletonSkillBuilder())
