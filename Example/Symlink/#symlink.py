
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import ctypes
import msvcrt
import configparser
import re

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def wait_exit():
    print("\n按任意键退出...")
    msvcrt.getch()
    sys.exit()

def sanitize_path(raw_path):
    clean_path = raw_path.strip('\"\'')
    return os.path.normpath(clean_path)

def load_config():
    config = configparser.ConfigParser()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "symlink.ini")
    
    if os.path.exists(config_path):
        try:
            config.read(config_path, encoding='utf-8-sig')
            config_dict = {
                'target_dir': sanitize_path(config.get('Path', 'Files')),
                'extensions': [x.strip().lower() for x in 
                             config.get('Path', 'ExName').split(',')],
                'output_dir': sanitize_path(config.get('Path', 'Output', fallback=script_dir))
            }
            
            if config.has_section('AutoCreat'):
                config_dict.update({
                    'auto_files': sanitize_path(config.get('AutoCreat', 'Files', fallback='')),
                    'auto_ext': config.get('AutoCreat', 'Exname', fallback='').strip().lower(),
                    'auto_output': sanitize_path(config.get('AutoCreat', 'Output', fallback=script_dir)),
                    'be_write': config.get('AutoCreat', 'BeWrite', fallback='').replace('/n', '\n'),
                    'use_auto': config.getint('AutoCreat', 'Use', fallback=0),
                    'custom_name': config.get('AutoCreat', 'Name', fallback='auto_created').strip('\"\'')
                })
            
            return config_dict
        except Exception as e:
            print(f"配置文件解析错误: {e}")
    return None

def auto_create_files(config):
    if not config.get('use_auto', 0):
        return
    
    target_dir = config['auto_files']
    ext = config['auto_ext']
    output_dir = config['auto_output']
    content = config.get('be_write', '')
    filename = f"{config['custom_name']}.{ext}" if config['custom_name'] else f"auto_created.{ext}"
    
    if not target_dir or not ext:
        print("\nAutoCreat配置不完整，跳过自动创建")
        return
    
    try:
        os.makedirs(target_dir, exist_ok=True)
        filepath = os.path.join(target_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if content:
                f.write(content)
        
        print(f"\n已创建文件: {filepath}")
        if content:
            print(f"已写入内容: {repr(content)}")
        
        os.makedirs(output_dir, exist_ok=True)
        dst = os.path.join(output_dir, filename)
        if os.path.exists(dst):
            os.remove(dst)
        os.symlink(filepath, dst)
        print(f"已创建符号链接: {dst}")
        
    except Exception as e:
        print(f"自动创建文件失败: {e}")

def get_user_input():
    while True:
        target_dir = input("请输入绝对路径：").strip()
        target_dir = sanitize_path(target_dir)
        if os.path.isdir(target_dir):
            break
        print(f"路径无效: {target_dir}")
    
    exts_input = input("请输入处理的扩展名（可多个，以,间隔）: ").strip()
    extensions = [ext.strip().lower() for ext in exts_input.split(',') if ext.strip()]
    
    return target_dir, extensions

def list_files(target_dir, extensions):
    files = []
    try:
        for f in os.listdir(target_dir):
            if os.path.isfile(os.path.join(target_dir, f)):
                ext = os.path.splitext(f)[1][1:].lower()
                if ext in extensions:
                    files.append(f)
    except Exception as e:
        print(f"文件扫描错误: {e}")
    return files

def create_symlinks(files, target_dir, output_dir):
    success = 0
    for i, filename in enumerate(files, 1):
        src = os.path.join(target_dir, filename)
        dst = os.path.join(output_dir, filename)
        
        try:
            if os.path.exists(dst):
                os.remove(dst)
            os.symlink(src, dst)
            print(f"[{i}] 成功创建: {filename}")
            success += 1
        except Exception as e:
            print(f"[{i}] 创建失败 {filename}: {e}")
    return success

def main():
    if not is_admin():
        print("错误：需要管理员权限运行")
        wait_exit()
    print("确认环境为管理员权限")

    config = load_config()
    if config:
        if config.get('use_auto', 0):
            auto_create_files(config)
            if input("\n自动创建完成，是否继续处理其他文件？(y/n): ").lower() != 'y':
                wait_exit()
        
        target_dir = config['target_dir']
        extensions = config['extensions']
        output_dir = config['output_dir']
        print(f"\n使用配置文件参数：\n路径: {target_dir}\n扩展名: {extensions}")
    else:
        target_dir, extensions = get_user_input()
        output_dir = os.path.dirname(os.path.abspath(__file__))

    files = list_files(target_dir, extensions)
    if not files:
        print(f"\n未找到 {extensions} 类型文件")
        wait_exit()

    print("\n检测到以下文件：")
    for i, f in enumerate(files, 1):
        print(f"{i} {f}")

    while True:
        choices = input("\n请选择处理的文件（序号）多个以,间隔: ").strip()
        try:
            selected = [int(c.strip())-1 for c in choices.split(',') if c.strip()]
            selected_files = [files[i] for i in selected if 0 <= i < len(files)]
            if selected_files:
                break
        except ValueError:
            pass
        print("错误：无效选择")

    success = create_symlinks(selected_files, target_dir, output_dir)
    print(f"\n处理完毕，成功创建 {success}/{len(selected_files)} 个符号链接")
    wait_exit()

if __name__ == "__main__":
    main()
