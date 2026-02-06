#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
玲珑应用更新检查工具

提供以下功能：
1. 提取已安装应用列表
2. 调用更新检查接口
3. 生成统计报告
4. 执行完整的更新检查流程
"""

import re
import json
import subprocess
import sys
from typing import List, Dict, Optional, Tuple


class LinglongUpdateChecker:
    """玲珑应用更新检查器"""
    
    def __init__(self, temp_dir='/tmp'):
        """
        初始化更新检查器
        
        Args:
            temp_dir: 临时文件目录
        """
        self.temp_dir = temp_dir
        self.list_file = f'{temp_dir}/ll_cli_list.txt'
        self.check_request_file = f'{temp_dir}/app_check_update.json'
        self.check_result_file = f'{temp_dir}/update_check_result.json'
        self.api_url = 'https://storeapi.linyaps.org.cn/app/appCheckUpdate'
        self.default_arch = 'x86_64'
    
    def get_installed_apps(self) -> bool:
        """
        使用ll-cli获取已安装应用列表
        
        Returns:
            bool: 是否成功获取
        """
        print("正在获取已安装应用列表...")
        
        try:
            result = subprocess.run(
                ['ll-cli', 'list'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                with open(self.list_file, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                print(f"已保存应用列表到 {self.list_file}")
                return True
            else:
                print(f"获取应用列表失败: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("错误: 未找到 ll-cli 命令")
            return False
        except Exception as e:
            print(f"获取应用列表时出错: {e}")
            return False
    
    def extract_installed_apps(self) -> List[Dict[str, str]]:
        """
        从ll-cli list输出中提取应用信息
        
        Returns:
            应用列表 [{"appId": "...", "arch": "...", "version": "..."}]
        """
        try:
            with open(self.list_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"错误: 未找到应用列表文件 {self.list_file}")
            return []
        
        # 移除ANSI颜色代码
        content = re.sub(r'\x1b\[[0-9;]*m', '', content)
        lines = content.split('\n')
        
        app_list = []
        for line in lines:
            # 跳过标题行和空行
            if not line.strip() or 'ID' in line or '名称' in line:
                continue
            
            # 匹配应用ID模式（以小写字母开头，包含点号的完整ID）
            app_match = re.match(r'([a-z][a-z0-9.-]+)', line)
            if app_match:
                app_id = app_match.group(1)
                
                # 查找版本号（数字.数字.数字模式）
                version_match = re.search(r'\b(\d+\.\d+[\d\.]*)\b', line)
                if version_match:
                    version = version_match.group(1)
                    
                    app_list.append({
                        "appId": app_id,
                        "arch": self.default_arch,
                        "version": version
                    })
        
        return app_list
    
    def save_check_request(self, app_list: List[Dict[str, str]]) -> bool:
        """
        保存更新检查请求到文件
        
        Args:
            app_list: 应用列表
            
        Returns:
            bool: 是否成功保存
        """
        try:
            with open(self.check_request_file, 'w', encoding='utf-8') as f:
                json.dump(app_list, f, ensure_ascii=False, indent=2)
            print(f"已保存更新检查请求到 {self.check_request_file}")
            return True
        except Exception as e:
            print(f"保存更新检查请求失败: {e}")
            return False
    
    def call_update_check_api(self) -> Optional[Dict]:
        """
        调用更新检查接口
        
        Returns:
            更新检查结果字典，失败返回None
        """
        print("正在检查更新...")
        
        try:
            result = subprocess.run([
                'curl', '-sS', '-X', 'POST',
                self.api_url,
                '-H', 'Content-Type: application/json',
                '-d', f'@{self.check_request_file}'
            ], capture_output=True, text=True, encoding='utf-8', timeout=30)
            
            if result.returncode == 0:
                try:
                    update_data = json.loads(result.stdout)
                    
                    with open(self.check_result_file, 'w', encoding='utf-8') as f:
                        json.dump(update_data, f, ensure_ascii=False, indent=2)
                    
                    print(f"更新检查完成，状态码: {update_data.get('code')}")
                    return update_data
                    
                except json.JSONDecodeError:
                    print("更新检查接口返回数据解析失败")
                    print("返回内容:", result.stdout[:200])
                    return None
            else:
                print(f"更新检查接口调用失败: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("更新检查接口调用超时")
            return None
        except Exception as e:
            print(f"调用更新检查接口时出错: {e}")
            return None
    
    def generate_report(self) -> Optional[Dict]:
        """
        生成应用统计与更新报告
        
        Returns:
            报告字典，失败返回None
        """
        # 读取更新检查结果
        try:
            with open(self.check_result_file, 'r', encoding='utf-8') as f:
                update_result = json.load(f)
        except FileNotFoundError:
            print(f"错误: 未找到更新检查结果文件 {self.check_result_file}")
            return None
        
        # 读取已安装的应用列表
        try:
            with open(self.list_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"错误: 未找到应用列表文件 {self.list_file}")
            return None
        
        content = re.sub(r'\x1b\[[0-9;]*m', '', content)
        lines = content.split('\n')
        
        # 构建可更新应用的ID集合和版本映射
        updateable_apps = {
            app['appId']: app['version'] 
            for app in update_result.get('data', [])
        }
        
        # 列出所有应用
        app_list = []
        for line in lines:
            if not line.strip() or 'ID' in line or '名称' in line:
                continue
            
            app_match = re.match(r'([a-z][a-z0-9.-]+)', line)
            if app_match:
                app_id = app_match.group(1)
                version_match = re.search(r'\b(\d+\.\d+[\d\.]*)\b', line)
                if version_match:
                    version = version_match.group(1)
                    is_runtime = 'runtime' in app_id.lower()
                    needs_update = app_id in updateable_apps
                    new_version = updateable_apps.get(app_id, '')
                    
                    app_list.append({
                        'appId': app_id,
                        'version': version,
                        'is_runtime': is_runtime,
                        'needs_update': needs_update,
                        'new_version': new_version
                    })
        
        # 按是否需要更新排序
        app_list.sort(key=lambda x: (not x['needs_update'], x['appId']))
        
        # 统计
        total_apps = len(app_list)
        runtime_count = sum(1 for app in app_list if app['is_runtime'])
        updateable_count = sum(1 for app in app_list if app['needs_update'])
        
        # 打印报告
        print('\n' + '=' * 120)
        print('玲珑应用安装与更新统计报告')
        print('=' * 120)
        print(f'\n已安装应用总数: {total_apps} 个')
        print(f'其中运行时环境: {runtime_count} 个')
        print(f'应用软件: {total_apps - runtime_count} 个')
        print(f'需要更新: {updateable_count} 个')
        
        # 显示需要更新的应用
        print('\n' + '=' * 120)
        print('【需要更新的应用】')
        print('=' * 120)
        
        count = 0
        for app in app_list:
            if app['needs_update']:
                count += 1
                update_info = next(
                    (u for u in update_result.get('data', []) 
                     if u['appId'] == app['appId']), 
                    None
                )
                category = update_info['categoryName'] if update_info else ''
                print(f'{count}. {app["appId"]} '
                      f'(当前版本: {app["version"]} → 最新版本: {app["new_version"]}) '
                      f'- 分类: {category}')
        
        # 显示已是最新版本的应用
        print('\n' + '=' * 120)
        print('【已是最新版本的应用】')
        print('=' * 120)
        
        count = 0
        for app in app_list:
            if not app['needs_update']:
                count += 1
                marker = ' [运行时]' if app['is_runtime'] else ''
                print(f'{count}. {app["appId"]} ({app["version"]}){marker}')
        
        # 更新建议
        print('\n' + '=' * 120)
        print('更新建议:')
        print('=' * 120)
        if updateable_count > 0:
            print('• 建议优先更新浏览器应用（Chrome、Edge）以获得更好的安全性和性能')
            print('• 大型应用更新包较大，可在网络空闲时更新')
            print('• 系统工具更新较小，建议及时更新')
        else:
            print('• 所有应用都是最新版本，无需更新')
        print('=' * 120)
        
        return {
            'total_apps': total_apps,
            'runtime_count': runtime_count,
            'updateable_count': updateable_count,
            'updateable_apps': [app for app in app_list if app['needs_update']],
            'up_to_date_apps': [app for app in app_list if not app['needs_update']]
        }
    
    def run_full_check(self) -> Optional[Dict]:
        """
        执行完整的更新检查流程
        
        Returns:
            报告字典，失败返回None
        """
        # 步骤1: 获取已安装应用列表
        if not self.get_installed_apps():
            return None
        
        # 步骤2: 提取应用信息
        app_list = self.extract_installed_apps()
        if not app_list:
            print("未找到已安装的应用")
            return None
        
        print(f"共提取 {len(app_list)} 个应用")
        
        # 步骤3: 保存更新检查请求
        if not self.save_check_request(app_list):
            return None
        
        # 步骤4: 调用更新检查接口
        update_result = self.call_update_check_api()
        if not update_result or update_result.get('code') != 200:
            print("更新检查失败")
            return None
        
        # 步骤5: 生成报告
        report = self.generate_report()
        
        if report:
            print(f"\n检查完成！发现 {report['updateable_count']} 个可更新的应用。")
        
        return report
    
    def get_updateable_app_ids(self) -> List[str]:
        """
        获取需要更新的应用ID列表
        
        Returns:
            需要更新的应用ID列表
        """
        report = self.generate_report()
        if report:
            return [app['appId'] for app in report['updateable_apps']]
        return []
    
    def format_size(self, size_bytes: int) -> str:
        """
        格式化文件大小
        
        Args:
            size_bytes: 字节数
            
        Returns:
            格式化后的大小字符串
        """
        if size_bytes > 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='玲珑应用更新检查工具')
    parser.add_argument(
        '--temp-dir',
        default='/tmp',
        help='临时文件目录（默认: /tmp）'
    )
    parser.add_argument(
        '--arch',
        default='x86_64',
        help='架构（默认: x86_64）'
    )
    parser.add_argument(
        '--action',
        choices=['check', 'list', 'ids'],
        default='check',
        help='执行的操作: check(完整检查), list(提取列表), ids(获取更新ID)'
    )
    
    args = parser.parse_args()
    
    # 创建检查器
    checker = LinglongUpdateChecker(temp_dir=args.temp_dir)
    checker.default_arch = args.arch
    
    # 执行操作
    if args.action == 'check':
        report = checker.run_full_check()
        sys.exit(0 if report else 1)
    elif args.action == 'list':
        if checker.get_installed_apps():
            app_list = checker.extract_installed_apps()
            for app in app_list:
                print(f"{app['appId']} - {app['version']}")
        sys.exit(0)
    elif args.action == 'ids':
        report = checker.run_full_check()
        if report:
            for app in report['updateable_apps']:
                print(app['appId'])
        sys.exit(0 if report else 1)


if __name__ == '__main__':
    main()
