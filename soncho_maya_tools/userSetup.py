import os
import sys
import maya.cmds as cmds
import maya.api.OpenMaya as om2
import maya.mel as mel


TOOLS_NAMES = "soncho_maya_tools"
SUPPORTED_MAYA_VERSIONS = [2024, 2025]
SUPPORTED_PYTHON_VERSION = "3"


def pre_settings():

    om2.MGlobal.displayInfo(f"***{TOOLS_NAMES} pre settings***")


def post_settings():
    install_mel_script()
    om2.MGlobal.displayInfo(f"***{TOOLS_NAMES} post settings***")


def install_mel_script():

    # TODO: execfiledで実行した場合に__file__が取れないため、暫定的に同階層に__file__.pyを置き、対応している
    import __file__

    print(__file__)
    mel_dir = os.path.join(os.path.dirname(__file__), "mel")
    mel_list = [_file for _file in os.listdir(mel_dir) if _file.endswith(".mel")]
    for mel_file in mel_list:
        mel_path = os.path.join(mel_dir, mel_file)
        mel.eval(f'source "{mel_path}"')


def main():
    current_maya_version = int(cmds.about(version=True))
    current_python_version = sys.version.split(" ")[0]

    if (
        current_python_version.startswith(SUPPORTED_PYTHON_VERSION)
        and current_maya_version in SUPPORTED_MAYA_VERSIONS
    ):
        cmds.evalDeferred(pre_settings, lowPriority=False)
        cmds.evalDeferred(post_settings, lowPriority=True)
    else:
        error_message = (
            f"Unsupported version. {TOOLS_NAMES}"
            f"supports Maya {SUPPORTED_MAYA_VERSIONS} "
            f"and Python {SUPPORTED_PYTHON_VERSION}."
        )
        om2.MGlobal.displayWarning(error_message)


if __name__ == "__main__":
    main()
