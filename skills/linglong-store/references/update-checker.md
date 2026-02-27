# 玲珑应用更新检查工具

该技能包含用于检查玲珑应用更新的Python工具脚本，脚本位于 `scripts/`。

## 工具列表

### linglong_update_checker.py

完整的更新检查工具，提供以下功能：

1. 提取已安装应用列表
2. 调用更新检查API
3. 生成统计报告
4. 执行完整的更新检查流程

## 安装

无需额外依赖，只需要Python 3.6+和以下系统工具：

- `ll-cli` - 玲珑命令行工具
- `curl` - 用于调用API

## 使用方法

### 基本使用

```bash
# 执行完整的更新检查流程
python3 .agents/skills/linglong-store/scripts/linglong_update_checker.py

# 指定临时文件目录
python3 .agents/skills/linglong-store/scripts/linglong_update_checker.py --temp-dir /path/to/temp

# 指定架构
python3 .agents/skills/linglong-store/scripts/linglong_update_checker.py --arch x86_64
```

### 可用操作

```bash
# check: 执行完整的更新检查流程（默认）
python3 .agents/skills/linglong-store/scripts/linglong_update_checker.py --action check

# list: 仅提取已安装应用列表
python3 .agents/skills/linglong-store/scripts/linglong_update_checker.py --action list

# ids: 获取需要更新的应用ID列表
python3 .agents/skills/linglong-store/scripts/linglong_update_checker.py --action ids
```

## 作为Python模块使用

```python
import os
import sys

# 将技能目录加入PYTHONPATH（从仓库根目录执行）
sys.path.insert(0, os.path.abspath(".agents/skills/linglong-store"))

from scripts.linglong_update_checker import LinglongUpdateChecker

# 创建检查器
checker = LinglongUpdateChecker(temp_dir='/tmp')

# 执行完整检查
report = checker.run_full_check()

if report:
    print(f"发现 {report['updateable_count']} 个可更新的应用")
    
    # 获取需要更新的应用ID
    updateable_ids = checker.get_updateable_app_ids()
    for app_id in updateable_ids:
        print(f"需要更新: {app_id}")
```

## 输出示例

```
玲珑应用安装与更新统计报告
========================================================================================================================

已安装应用总数: 46 个
其中运行时环境: 8 个
应用软件: 38 个
需要更新: 7 个

========================================================================================================================
【需要更新的应用】
========================================================================================================================
1. cn.google.chrome (当前版本: 143.0.7499.109 → 最新版本: 144.0.7559.109) - 分类: 网络应用
2. cn.wps.wps-office (当前版本: 12.1.2.23579 → 最新版本: 12.1.2.24722) - 分类: 效率办公
...

========================================================================================================================
【已是最新版本的应用】
========================================================================================================================
1. cn.com.10jqka (2.7.1.4)
2. cn.org.linyaps.preloader (25.2.0.4)
...

========================================================================================================================
更新建议:
========================================================================================================================
• 建议优先更新浏览器应用（Chrome、Edge）以获得更好的安全性和性能
• 大型应用更新包较大，可在网络空闲时更新
• 系统工具更新较小，建议及时更新
========================================================================================================================
```

## 文件说明

- `scripts/linglong_update_checker.py` - 主工具脚本
- `references/update-checker.md` - 本说明文档

## 依赖

- Python 3.6+
- `ll-cli` 命令行工具
- `curl` 命令

## 注意事项

1. 确保 `ll-cli` 命令可用
2. 确保网络连接正常（需要调用API）
3. 默认使用 `x86_64` 架构，如需其他架构请使用 `--arch` 参数指定
4. 临时文件默认保存在 `/tmp` 目录

## 故障排查

### 问题: 找不到 ll-cli 命令

**解决方案**: 确保已安装玲珑运行时环境，并且 `ll-cli` 在系统PATH中。

### 问题: 更新检查接口调用失败

**解决方案**: 
1. 检查网络连接
2. 确认API地址 `https://storeapi.linyaps.org.cn/app/appCheckUpdate` 可访问
3. 查看临时文件中的详细错误信息

### 问题: 解析应用列表失败

**解决方案**: 
1. 检查 `ll-cli list` 命令的输出格式是否正确
2. 查看临时文件 `/tmp/ll_cli_list.txt` 的内容
