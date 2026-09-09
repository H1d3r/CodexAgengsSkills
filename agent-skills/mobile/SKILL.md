---
name: mobile
description: Apply iOS and Android lifecycle, permissions, state, networking, accessibility, and release-aware practices.
---

# Mobile (iOS / Android) Skill（for Agents）

## 适用场景
- Android Native（Kotlin/Java）、iOS（Swift）
- Flutter / React Native 等跨端项目维护与排障
- 上线、隐私、离线、性能、生命周期类问题

## 核心原则

1. **生命周期优先**：先确认页面/Activity/ViewController 生命周期再改生命周期逻辑。
2. **最小改动**：优先修复可见缺陷，不做大范围架构迁移。
3. **用户端体验优先**：首帧、崩溃率、耗电与权限体验要可验证。

## 强制执行清单

- 权限申请要明确时机、用途说明、失败兜底。
- 异常与崩溃日志带 `user/device/version/session`。
- 网络、存储、位置等敏感操作遵循最小权限与最小频率。
- 离线/弱网场景有降级与重试策略。
- 发布前检查证书、签名、版本号、兼容性配置。

## 常见实践

- Android：避免生命周期泄漏（ViewModel 生命周期边界、协程取消）。
- iOS：避免 retain cycle，优先 `weak/unowned` 处理闭包引用。
- Flutter：区分 build 与副作用逻辑，避免重复构建导致状态错乱。
- RN：原生模块调用要有超时与异常处理。

## 常用质量门禁

- `./gradlew test` / `./gradlew lint`
- `xcodebuild test` / `xcodebuild` 打包校验
- Crash-free 指标监控、ANR/Crash 日志归因
- 自动化 UI 流程（如有）与安装/签名校验

## 反模式（避免）

- 在主线程做重计算/解码引发掉帧。
- 忽略权限被拒绝分支，直接调用受保护 API。
- 网络请求与数据库操作未与 UI 生命周期解绑。
- 热修复/更新流程未验证签名与回滚链路。

## 与仓库冲突时的优先级

- 以 Gradle/Xcode/Flutter/CI 配置与发布流程为准。
- 与本文件冲突时按平台发布与审核规范执行。
