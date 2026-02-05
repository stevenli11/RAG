# 如何使用 V1.1.0 发布文档 / How to Use V1.1.0 Release Documentation

## 📋 文档概览 / Document Overview

本次为 RAG 项目创建了完整的 V1.1.0 版本发布文档，包含以下文件：

This release includes complete V1.1.0 documentation with the following files:

### 核心文档 / Core Documents

1. **VERSION** - 版本号文件 / Version number file
   - 内容：`1.1.0`
   - 用途：简单的版本标识

2. **CHANGELOG.md** - 变更日志 / Changelog
   - 格式：遵循 Keep a Changelog 标准
   - 语言：英文
   - 用途：详细记录所有版本的变更历史

3. **RELEASES.md** - 发布说明（中文）/ Release Notes (Chinese)
   - 格式：中文详细说明
   - 内容：V1.1.0 的功能描述、技术亮点、使用建议
   - 用途：面向中文用户的发布说明

4. **RELEASE_NOTES_V1.1.md** - 发布说明（英文）/ Release Notes (English)
   - 格式：英文详细说明
   - 内容：完整的功能介绍、技术细节、使用说明
   - 用途：GitHub Release 的主要内容来源

5. **RELEASE_V1.1_SUMMARY.txt** - 发布摘要 / Release Summary
   - 格式：纯文本格式
   - 内容：快速参考的摘要信息
   - 用途：快速查看发布概况

6. **.github/RELEASE_GUIDE.md** - 发布指南 / Release Guide
   - 内容：如何创建 GitHub Release 的步骤
   - 用途：指导维护者创建正式发布

7. **README.md** - 项目说明（已更新）/ Project README (Updated)
   - 新增：V1.1 版本标识和新功能亮点
   - 新增：版本历史链接

## 🎯 V1.1.0 新功能 / New Features

### 1. OCR 模型支持 📸
- 支持图片文件上传（JPG, PNG, BMP, TIFF）
- 自动识别扫描版 PDF
- 智能回退机制
- 使用 DashScope qwen-vl-max 模型

### 2. 问题分类系统 🧠
- 自动分类为三类：知识类、实验类、通用类
- 根据分类动态选择 prompt
- 提高回答的准确性和相关性

## 📝 如何创建 GitHub Release / How to Create GitHub Release

### 方法 1：GitHub 网页界面（推荐）

1. 访问仓库：https://github.com/stevenli11/RAG
2. 点击右侧的 "Releases"
3. 点击 "Draft a new release"
4. 填写信息：
   - **Tag**: `v1.1.0`
   - **Title**: `V1.1.0 - OCR Support & Intelligent Question Classification`
   - **Description**: 复制 `RELEASE_NOTES_V1.1.md` 的内容
5. 点击 "Publish release"

### 方法 2：使用 GitHub CLI

```bash
gh release create v1.1.0 \
  --title "V1.1.0 - OCR Support & Intelligent Question Classification" \
  --notes-file RELEASE_NOTES_V1.1.md
```

## 📚 文档使用建议 / Documentation Usage Tips

### 对于维护者 / For Maintainers
- 使用 `RELEASE_NOTES_V1.1.md` 作为 GitHub Release 的描述
- 参考 `.github/RELEASE_GUIDE.md` 了解发布步骤
- 查看 `RELEASE_V1.1_SUMMARY.txt` 快速了解发布内容

### 对于中文用户 / For Chinese Users
- 阅读 `RELEASES.md` 获取中文版本说明
- 包含详细的功能描述和使用建议

### 对于英文用户 / For English Users
- 查看 `RELEASE_NOTES_V1.1.md` 获取完整的英文说明
- 包含技术细节和使用指南

### 对于开发者 / For Developers
- 查看 `CHANGELOG.md` 了解所有版本的技术变更
- 遵循标准的 changelog 格式

## ✅ 检查清单 / Checklist

发布前确认 / Pre-release confirmation:

- [x] VERSION 文件已创建
- [x] CHANGELOG.md 已创建并记录 V1.1.0
- [x] RELEASES.md 中文说明已创建
- [x] RELEASE_NOTES_V1.1.md 英文说明已创建
- [x] README.md 已更新版本信息
- [x] 发布指南已创建
- [x] 代码中的功能已验证存在
- [x] 所有文件已提交并推送

## 🚀 下一步 / Next Steps

1. **创建 GitHub Release** - 使用上述方法之一
2. **验证 Release** - 确认 Release 页面显示正确
3. **通知用户** - 可选，向用户发布更新通知
4. **更新其他文档** - 如需要，更新项目相关的外部文档

## 📞 支持 / Support

如有问题，请：
- 查看各个文档文件获取详细信息
- 参考 `.github/RELEASE_GUIDE.md` 了解发布步骤
- 查看代码中的实际实现（app.py）

For questions:
- Check the documentation files for details
- Refer to `.github/RELEASE_GUIDE.md` for release steps
- Review the actual implementation in code (app.py)
