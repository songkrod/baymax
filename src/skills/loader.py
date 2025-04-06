# src/skills/loader.py

import os
import importlib.util
from utils.logger import logger

SKILLS_ROOT = "src/skills"

SKILL_REGISTRY = {}


def load_skill(skill_filename: str) -> dict:
    """
    โหลด skill จากไฟล์ .py โดยอัตโนมัติ และบอกแหล่งที่มาของ skill นั้น
    """
    for folder_name in os.listdir(SKILLS_ROOT):
        folder_path = os.path.join(SKILLS_ROOT, folder_name)
        if not os.path.isdir(folder_path):
            continue

        full_path = os.path.join(folder_path, skill_filename)
        if os.path.exists(full_path):
            try:
                module_name = f"skills.{folder_name}.{os.path.splitext(skill_filename)[0]}"

                spec = importlib.util.spec_from_file_location(module_name, full_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    SKILL_REGISTRY[skill_filename] = {
                        "module": module,
                        "source": folder_name
                    }
                    logger.info(f"[⚙️] โหลด skill สำเร็จ: {skill_filename} ({folder_name})")
                    return {
                        "name": skill_filename,
                        "source": folder_name,
                        "module": module
                    }
            except Exception as e:
                logger.error(f"[❌] โหลด skill ล้มเหลว: {skill_filename} ({e})")
                raise e

    raise FileNotFoundError(f"Skill ไม่พบใน folders ทั้งหมด: {skill_filename}")


def get_loaded_skills() -> dict:
    return SKILL_REGISTRY
