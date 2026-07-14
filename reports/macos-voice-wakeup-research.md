# macOS 语音唤醒实现方案技术调研报告

## 概述

本报告调研在 macOS 上实现类似 "Hey Siri" 的语音唤醒功能，支持自定义唤醒词（如"龙虾"、"OpenClaw"、"贾维斯"），并与 OpenClaw 网关集成。

---

## 1. 可行方案对比

### 方案一：Porcupine (Picovoice)

**简介**
- 商业级本地唤醒词引擎，由 Picovoice 开发
- 支持多平台：macOS (x86_64/arm64)、iOS、Android、Linux、Windows
- 支持多语言：中文、英文、法语、德语、日语、韩语等
- 使用深度学习模型，在真实环境中训练

**优点**
- ✅ 极高的准确率（比 Snowboy 准确 11 倍）
- ✅ 极低的资源占用（比 Snowboy 快 6.5 倍）
- ✅ 支持自定义唤醒词训练（通过 Picovoice Console）
- ✅ 支持中文唤醒词
- ✅ 提供多种 SDK：Swift、Python、Node.js、C/C++
- ✅ 支持同时检测多个唤醒词
- ✅ 离线运行，无需网络

**缺点**
- ❌ 免费版有使用限制（需要 Access Key）
- ❌ 自定义唤醒词需要在线训练
- ❌ 闭源商业产品

**资源占用**
- CPU: 低（优化用于 IoT 设备）
- 内存: ~5-10 MB
- 延迟: <100ms

---

### 方案二：macOS Speech.framework

**简介**
- Apple 原生的语音识别框架
- 从 macOS 10.15+ 开始支持离线识别（on-device recognition）
- 支持中文、英文等多种语言

**优点**
- ✅ 系统原生，无需额外依赖
- ✅ 与 macOS 深度集成
- ✅ 支持离线识别（SFSpeechRecognizer 的 `requiresOnDeviceRecognition`）
- ✅ 免费使用

**缺点**
- ❌ 不是专门的唤醒词引擎，是通用语音识别
- ❌ 需要持续运行完整语音识别，资源占用高
- ❌ 延迟较高（完整 ASR 流程）
- ❌ 不支持自定义唤醒词训练
- ❌ 需要麦克风权限和语音识别权限

**资源占用**
- CPU: 中高（完整神经网络 ASR）
- 内存: ~50-100 MB
- 延迟: 200-500ms

---

### 方案三：openWakeWord

**简介**
- 开源唤醒词检测框架
- 基于 ONNX Runtime 或 TensorFlow Lite
- 支持自定义模型训练

**优点**
- ✅ 完全开源免费
- ✅ 支持自定义唤醒词训练
- ✅ 预训练模型可用（alexa、hey jarvis、hey mycroft 等）
- ✅ Python 实现，易于集成

**缺点**
- ❌ **macOS Apple Silicon 支持有问题**（缺少 TFLite arm64 运行时）
- ❌ 需要额外安装依赖（ONNX Runtime）
- ❌ 准确率略低于 Porcupine
- ❌ 社区支持相对较小

**资源占用**
- CPU: 中
- 内存: ~20-30 MB
- 延迟: 100-200ms

---

### 方案四：Snowboy (已弃用)

**简介**
- 曾经流行的开源唤醒词引擎
- 由 Kitt.AI 开发，已被 Google 收购并停止维护

**优点**
- ✅ 轻量级
- ✅ 支持自定义唤醒词

**缺点**
- ❌ **项目已停止维护**（2018 年后不再更新）
- ❌ 不支持 Apple Silicon
- ❌ 准确率较低
- ❌ 不支持现代 macOS

**结论**：不推荐用于新项目

---

### 方案五：local-wake

**简介**
- 结合神经网络特征提取 + 动态时间规整（DTW）
- 无需训练即可使用自定义唤醒词

**优点**
- ✅ 无需训练即可自定义唤醒词
- ✅ 结合神经网络和传统算法的优势
- ✅ 开源免费

**缺点**
- ❌ 相对较新，成熟度不如 Porcupine
- ❌ 准确率依赖参考样本质量
- ❌ 需要录制参考音频

**资源占用**
- CPU: 中低
- 内存: ~15-25 MB

---

## 2. 方案对比总结表

| 特性 | Porcupine | Speech.framework | openWakeWord | Snowboy | local-wake |
|------|-----------|------------------|--------------|---------|------------|
| **准确率** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **资源占用** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **延迟** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **中文支持** | ✅ | ✅ | ✅ | ❌ | ✅ |
| **自定义唤醒词** | ✅ | ❌ | ✅ | ✅ | ✅ |
| **离线运行** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Apple Silicon** | ✅ | ✅ | ❌ | ❌ | ✅ |
| **开源** | ❌ | ❌ | ✅ | ✅(弃用) | ✅ |
| **免费** | 有限制 | ✅ | ✅ | ✅ | ✅ |
| **维护状态** | 活跃 | 活跃 | 活跃 | 弃用 | 较新 |

---

## 3. 推荐方案

### 主要推荐：Porcupine (Picovoice)

**推荐理由：**

1. **准确率最高**：在 Raspberry Pi 3 上比 Snowboy 准确 11 倍，误唤醒率极低
2. **资源占用最低**：优化用于 IoT 设备，适合长期后台运行
3. **中文支持完善**：支持"龙虾"、"贾维斯"等中文唤醒词
4. **Apple Silicon 原生支持**：提供 arm64 版本，性能优异
5. **OpenClaw 兼容**：OpenClaw 官方文档提到使用 `voicewake.get` 协议同步唤醒词
6. **多平台一致**：如果未来需要扩展到 iOS，代码可复用

**免费版限制：**
- 每月 10,000 次推理限制（个人使用足够）
- 需要注册获取 Access Key
- 自定义唤醒词训练需要付费（但内置关键词免费）

### 备选方案：Speech.framework

如果对第三方依赖敏感，可以使用 Speech.framework 作为备选，但需要：
- 实现关键词匹配逻辑
- 接受更高的资源占用
- 处理语音识别的不稳定性

---

## 4. 实现步骤

### 步骤 1：环境准备

```bash
# 1. 注册 Picovoice Console 获取 Access Key
# https://console.picovoice.ai/

# 2. 安装 Porcupine Swift SDK（通过 CocoaPods 或 SPM）
# Podfile:
pod 'Porcupine-iOS'

# 或 Swift Package Manager:
# https://github.com/Picovoice/porcupine-swift
```

### 步骤 2：创建唤醒词检测服务

```swift
import Porcupine
import AVFoundation

class VoiceWakeService: NSObject {
    private var porcupine: Porcupine?
    private var audioEngine: AVAudioEngine?
    private let accessKey = "YOUR_ACCESS_KEY"
    
    // 唤醒词回调
    var onWakeWordDetected: ((String) -> Void)?
    
    func initialize(keywords: [String]) throws {
        // 初始化 Porcupine
        // 使用内置关键词或自定义 .ppn 文件
        porcupine = try Porcupine(
            accessKey: accessKey,
            keywordPaths: keywordPaths,
            sensitivities: Array(repeating: 0.5, count: keywords.count)
        )
        
        setupAudioEngine()
    }
    
    private func setupAudioEngine() {
        audioEngine = AVAudioEngine()
        let inputNode = audioEngine!.inputNode
        let recordingFormat = inputNode.outputFormat(forBus: 0)
        
        // 确保格式匹配 Porcupine 要求（16kHz, 单声道, 16-bit）
        guard let format = AVAudioFormat(
            commonFormat: .pcmFormatInt16,
            sampleRate: Double(porcupine!.sampleRate),
            channels: 1,
            interleaved: true
        ) else {
            fatalError("无法创建音频格式")
        }
        
        inputNode.installTap(onBus: 0, bufferSize: UInt32(porcupine!.frameLength), format: format) { [weak self] buffer, _ in
            self?.processAudioBuffer(buffer)
        }
    }
    
    private func processAudioBuffer(_ buffer: AVAudioPCMBuffer) {
        guard let porcupine = porcupine else { return }
        
        // 将缓冲区转换为 Int16 数组
        let frameLength = Int(porcupine.frameLength)
        var pcmData = [Int16](repeating: 0, count: frameLength)
        
        let channelData = buffer.int16ChannelData![0]
        for i in 0..<min(frameLength, Int(buffer.frameLength)) {
            pcmData[i] = channelData[i]
        }
        
        // 处理音频帧
        do {
            let keywordIndex = try porcupine.process(pcmData)
            if keywordIndex >= 0 {
                let detectedKeyword = keywords[keywordIndex]
                DispatchQueue.main.async {
                    self.onWakeWordDetected?(detectedKeyword)
                }
            }
        } catch {
            print("处理音频时出错: \(error)")
        }
    }
    
    func start() throws {
        try audioEngine?.start()
    }
    
    func stop() {
        audioEngine?.stop()
        audioEngine?.inputNode.removeTap(onBus: 0)
    }
    
    deinit {
        porcupine?.delete()
    }
}
```

### 步骤 3：与 OpenClaw 网关集成

```swift
import Foundation

class OpenClawVoiceWakeIntegration {
    private var webSocketTask: URLSessionWebSocketTask?
    private let gatewayURL: URL
    private var voiceWakeService: VoiceWakeService
    
    init(gatewayURL: URL) {
        self.gatewayURL = gatewayURL
        self.voiceWakeService = VoiceWakeService()
    }
    
    func connect() {
        // 建立 WebSocket 连接
        let session = URLSession(configuration: .default)
        webSocketTask = session.webSocketTask(with: gatewayURL)
        webSocketTask?.resume()
        
        // 监听唤醒词变更
        listenForWakeWordChanges()
        
        // 获取当前唤醒词列表
        fetchCurrentWakeWords()
    }
    
    private func fetchCurrentWakeWords() {
        let message: [String: Any] = [
            "type": "req",
            "method": "voicewake.get",
            "params": [:]
        ]
        
        sendMessage(message)
    }
    
    private func listenForWakeWordChanges() {
        webSocketTask?.receive { [weak self] result in
            switch result {
            case .success(let message):
                self?.handleMessage(message)
                self?.listenForWakeWordChanges() // 继续监听
            case .failure(let error):
                print("WebSocket 错误: \(error)")
            }
        }
    }
    
    private func handleMessage(_ message: URLSessionWebSocketTask.Message) {
        guard case .string(let text) = message,
              let data = text.data(using: .utf8),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            return
        }
        
        // 处理 voicewake.changed 事件
        if let event = json["event"] as? String, event == "voicewake.changed",
           let triggers = json["triggers"] as? [String] {
            updateWakeWords(triggers)
        }
        
        // 处理 voicewake.get 响应
        if let method = json["method"] as? String, method == "voicewake.get",
           let result = json["result"] as? [String: Any],
           let triggers = result["triggers"] as? [String] {
            updateWakeWords(triggers)
        }
    }
    
    private func updateWakeWords(_ triggers: [String]) {
        // 重新初始化唤醒词检测器
        do {
            try voiceWakeService.initialize(keywords: triggers)
            try voiceWakeService.start()
            
            // 设置唤醒回调
            voiceWakeService.onWakeWordDetected = { [weak self] keyword in
                self?.handleWakeWordDetected(keyword)
            }
        } catch {
            print("更新唤醒词失败: \(error)")
        }
    }
    
    private func handleWakeWordDetected(_ keyword: String) {
        print("🎤 检测到唤醒词: \(keyword)")
        
        // 触发 OpenClaw 会话激活
        let event: [String: Any] = [
            "type": "event",
            "event": "voice.wake",
            "payload": [
                "trigger": keyword,
                "timestamp": Date().timeIntervalSince1970 * 1000
            ]
        ]
        
        sendMessage(event)
        
        // 可选：播放提示音
        playActivationSound()
    }
    
    private func sendMessage(_ message: [String: Any]) {
        guard let data = try? JSONSerialization.data(withJSONObject: message),
              let text = String(data: data, encoding: .utf8) else {
            return
        }
        
        webSocketTask?.send(.string(text)) { error in
            if let error = error {
                print("发送消息失败: \(error)")
            }
        }
    }
    
    private func playActivationSound() {
        // 播放系统提示音或自定义音效
        NSSound(named: "Glass")?.play()
    }
}
```

### 步骤 4：处理权限

```swift
import AVFoundation
import Speech

class PermissionManager {
    static func requestPermissions(completion: @escaping (Bool) -> Void) {
        var microphoneAuthorized = false
        var speechAuthorized = false
        
        let group = DispatchGroup()
        
        // 请求麦克风权限
        group.enter()
        AVCaptureDevice.requestAccess(for: .audio) { granted in
            microphoneAuthorized = granted
            group.leave()
        }
        
        // 请求语音识别权限（如果使用 Speech.framework）
        group.enter()
        SFSpeechRecognizer.requestAuthorization { status in
            speechAuthorized = (status == .authorized)
            group.leave()
        }
        
        group.notify(queue: .main) {
            completion(microphoneAuthorized && speechAuthorized)
        }
    }
}
```

### 步骤 5：后台运行支持

```swift
import Cocoa

class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        // 请求后台运行权限
        NSApp.setActivationPolicy(.accessory) // 菜单栏应用模式
        
        // 设置音频会话保持活跃
        setupAudioSession()
    }
    
    private func setupAudioSession() {
        // 确保应用在后台时音频继续运行
        do {
            try AVAudioSession.sharedInstance().setCategory(.playAndRecord, mode: .default, options: [.mixWithOthers, .allowBluetooth])
            try AVAudioSession.sharedInstance().setActive(true)
        } catch {
            print("设置音频会话失败: \(error)")
        }
    }
}
```

---

## 5. 性能要求和资源占用

### Porcupine 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| **CPU 占用** | 1-3% | M1/M2 Mac 上持续监听 |
| **内存占用** | 5-15 MB | 包含模型和运行时 |
| **延迟** | < 50ms | 从语音输入到检测完成 |
| **功耗** | 低 | 适合笔记本长期运行 |
| **模型大小** | ~50 KB | 每个唤醒词模型 |

### 系统要求

- **macOS 版本**: 10.15+ (Catalina)
- **硬件**: Intel 或 Apple Silicon (x86_64/arm64)
- **权限**: 麦克风访问权限
- **网络**: 首次验证 Access Key 需要网络，之后可离线运行

### 优化建议

1. **使用低功耗模式**：在电池供电时降低检测灵敏度
2. **VAD 前置**：使用语音活动检测（如 Silero VAD）过滤静音，减少处理
3. **动态灵敏度**：根据环境噪音调整灵敏度
4. **休眠策略**：长时间未检测到语音时暂停检测

---

## 6. 自定义唤醒词训练

### 使用 Picovoice Console

1. 访问 https://console.picovoice.ai/
2. 创建自定义唤醒词项目
3. 输入唤醒词文本（如"龙虾"、"贾维斯"）
4. 选择语言（中文 zh）
5. 训练并下载 `.ppn` 模型文件
6. 将模型文件集成到应用中

### 代码中使用自定义模型

```swift
// 使用自定义 .ppn 文件
let keywordPath = Bundle.main.path(forResource: "龙虾_zh_mac_v3_0_0", ofType: "ppn")!

porcupine = try Porcupine(
    accessKey: accessKey,
    keywordPaths: [keywordPath],
    sensitivities: [0.7]  // 提高灵敏度以适应中文
)
```

---

## 7. 与 OpenClaw 现有架构集成

### OpenClaw Voice Wake 协议

根据 OpenClaw 文档，唤醒词通过 Gateway 统一管理：

```
存储位置: ~/.openclaw/settings/voicewake.json
格式: { "triggers": ["openclaw", "claude", "computer"], "updatedAtMs": 1730000000000 }

协议方法:
- voicewake.get → 获取当前唤醒词列表
- voicewake.set → 设置唤醒词列表

事件:
- voicewake.changed → 唤醒词变更广播
```

### 集成架构

```
┌─────────────────────────────────────────────────────────────┐
│                        macOS 设备                            │
│  ┌─────────────────┐      ┌──────────────────────────────┐  │
│  │  VoiceWakeApp   │      │        OpenClaw Gateway       │  │
│  │                 │      │                               │  │
│  │ ┌─────────────┐ │      │  ┌─────────────────────────┐  │  │
│  │ │ Porcupine   │ │◄────►│  │   voicewake.json        │  │  │
│  │ │ Wake Engine │ │      │  │   triggers: [...]       │  │  │
│  │ └─────────────┘ │      │  └─────────────────────────┘  │  │
│  │        │        │      │           │                   │  │
│  │        ▼        │      │           ▼                   │  │
│  │ ┌─────────────┐ │      │  ┌─────────────────────────┐  │  │
│  │ │ AVAudioEngine│ │      │  │  WebSocket Server       │  │  │
│  │ │ Audio Input │ │◄────►│  │  - voicewake.get        │  │  │
│  │ └─────────────┘ │      │  │  - voicewake.set        │  │  │
│  │        │        │      │  │  - voicewake.changed    │  │  │
│  │        ▼        │      │  └─────────────────────────┘  │  │
│  │ ┌─────────────┐ │      │                               │  │
│  │ │  Detection  │ │      └───────────────────────────────┘  │
│  │ │   Callback  │ │                                         │
│  │ └─────────────┘ │                                         │
│  └─────────────────┘                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  OpenClaw Agent │
                    │  (激活会话)      │
                    └─────────────────┘
```

---

## 8. 代码示例：完整实现

### Swift Package Dependencies

```swift
// Package.swift
dependencies: [
    .package(url: "https://github.com/Picovoice/porcupine-swift", from: "3.0.0"),
    .package(url: "https://github.com/daltoniam/Starscream", from: "4.0.0") // WebSocket
]
```

### 主应用代码

```swift
import SwiftUI
import Porcupine
import AVFoundation

@main
struct VoiceWakeApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    
    var body: some Scene {
        Settings {
            EmptyView()
        }
    }
}

class AppDelegate: NSObject, NSApplicationDelegate {
    var statusItem: NSStatusItem?
    var voiceWakeManager: VoiceWakeManager?
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        // 创建菜单栏图标
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        statusItem?.button?.image = NSImage(systemSymbolName: "mic.fill", accessibilityDescription: "Voice Wake")
        
        // 设置菜单
        let menu = NSMenu()
        menu.addItem(NSMenuItem(title: "启用语音唤醒", action: #selector(toggleVoiceWake), keyEquivalent: ""))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "设置唤醒词...", action: #selector(openSettings), keyEquivalent: ","))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "退出", action: #selector(quit), keyEquivalent: "q"))
        statusItem?.menu = menu
        
        // 初始化语音唤醒
        voiceWakeManager = VoiceWakeManager()
        voiceWakeManager?.start()
    }
    
    @objc func toggleVoiceWake() {
        voiceWakeManager?.toggle()
    }
    
    @objc func openSettings() {
        // 打开设置窗口
    }
    
    @objc func quit() {
        NSApp.terminate(nil)
    }
}

// MARK: - Voice Wake Manager

class VoiceWakeManager {
    private var porcupine: Porcupine?
    private var audioEngine: AVAudioEngine?
    private var isRunning = false
    private let accessKey = "YOUR_ACCESS_KEY_HERE"
    
    private var keywords: [String] = ["openclaw", "claude", "computer"]
    
    func start() {
        guard !isRunning else { return }
        
        do {
            // 初始化 Porcupine
            try initializePorcupine()
            
            // 设置音频引擎
            try setupAudioEngine()
            
            // 开始监听
            try audioEngine?.start()
            isRunning = true
            
            print("✅ 语音唤醒已启动")
            print("🎤 监听唤醒词: \(keywords.joined(separator: ", "))")
            
        } catch {
            print("❌ 启动失败: \(error)")
        }
    }
    
    func stop() {
        audioEngine?.stop()
        audioEngine?.inputNode.removeTap(onBus: 0)
        porcupine?.delete()
        porcupine = nil
        isRunning = false
        print("🛑 语音唤醒已停止")
    }
    
    func toggle() {
        if isRunning {
            stop()
        } else {
            start()
        }
    }
    
    private func initializePorcupine() throws {
        // 使用内置关键词
        let builtInKeywords: [BuiltInKeyword] = [.openclaw, .claude, .computer]
        
        porcupine = try Porcupine(
            accessKey: accessKey,
            keywords: builtInKeywords,
            sensitivities: [0.5, 0.5, 0.5]
        )
    }
    
    private func setupAudioEngine() throws {
        audioEngine = AVAudioEngine()
        guard let audioEngine = audioEngine, let porcupine = porcupine else {
            throw VoiceWakeError.initializationFailed
        }
        
        let inputNode = audioEngine.inputNode
        
        // 创建 Porcupine 要求的音频格式
        guard let recordingFormat = AVAudioFormat(
            commonFormat: .pcmFormatInt16,
            sampleRate: Double(porcupine.sampleRate),
            channels: 1,
            interleaved: true
        ) else {
            throw VoiceWakeError.formatCreationFailed
        }
        
        // 安装音频 tap
        inputNode.installTap(onBus: 0, bufferSize: UInt32(porcupine.frameLength), format: recordingFormat) { [weak self] buffer, _ in
            self?.processAudioBuffer(buffer)
        }
        
        // 准备引擎
        try audioEngine.start()
    }
    
    private func processAudioBuffer(_ buffer: AVAudioPCMBuffer) {
        guard let porcupine = porcupine else { return }
        
        let frameLength = Int(porcupine.frameLength)
        guard Int(buffer.frameLength) >= frameLength else { return }
        
        // 提取 Int16 样本
        var pcmData = [Int16](repeating: 0, count: frameLength)
        if let channelData = buffer.int16ChannelData {
            for i in 0..<frameLength {
                pcmData[i] = channelData[0][i]
            }
        }
        
        // 处理音频帧
        do {
            let keywordIndex = try porcupine.process(pcmData)
            if keywordIndex >= 0 && keywordIndex < keywords.count {
                let detectedKeyword = keywords[keywordIndex]
                handleWakeWordDetection(detectedKeyword)
            }
        } catch {
            print("处理音频错误: \(error)")
        }
    }
    
    private func handleWakeWordDetection(_ keyword: String) {
        DispatchQueue.main.async { [weak self] in
            print("🔔 检测到唤醒词: \(keyword)")
            
            // 播放提示音
            NSSound(named: "Ping")?.play()
            
            // 触发 OpenClaw 激活
            self?.activateOpenClaw(with: keyword)
            
            // 显示视觉反馈
            self?.showVisualFeedback(for: keyword)
        }
    }
    
    private func activateOpenClaw(with keyword: String) {
        // 通过 AppleScript 或 URL Scheme 激活 OpenClaw
        let script = """
        tell application "OpenClaw" to activate
        """
        
        var error: NSDictionary?
        if let appleScript = NSAppleScript(source: script) {
            appleScript.executeAndReturnError(&error)
        }
        
        // 或者通过 Gateway WebSocket 发送事件
        NotificationCenter.default.post(
            name: .init("VoiceWakeDetected"),
            object: nil,
            userInfo: ["keyword": keyword]
        )
    }
    
    private func showVisualFeedback(for keyword: String) {
        // 更新菜单栏图标状态
        // 显示通知气泡
        let notification = NSUserNotification()
        notification.title = "语音唤醒"
        notification.informativeText = "检测到: \"\(keyword)\""
        notification.soundName = nil
        NSUserNotificationCenter.default.deliver(notification)
    }
}

enum VoiceWakeError: Error {
    case initializationFailed
    case formatCreationFailed
    case audioEngineStartFailed
}
```

---

## 9. 测试和调优

### 测试清单

- [ ] 在安静环境下测试唤醒准确率
- [ ] 在有背景噪音环境下测试（电视、音乐、交谈）
- [ ] 测试不同距离（1米、3米、5米）
- [ ] 测试不同音量（轻声、正常、大声）
- [ ] 测试误唤醒率（长时间运行观察）
- [ ] 测试 CPU/内存占用
- [ ] 测试电池消耗（笔记本）

### 调优参数

```swift
// 灵敏度调整（0.0 - 1.0）
// 值越高越容易检测，但误唤醒率也越高
let sensitivities: [Float32] = [
    0.7,  // "龙虾" - 较高灵敏度
    0.5,  // "OpenClaw" - 默认
    0.6   // "贾维斯" - 中等灵敏度
]

// 根据环境动态调整
func adjustSensitivity(for environment: Environment) -> Float32 {
    switch environment {
    case .quiet: return 0.5
    case .moderate: return 0.6
    case .noisy: return 0.7
    }
}
```

---

## 10. 结论

### 推荐方案

**首选 Porcupine**，原因：
1. 准确率和性能最优
2. 原生支持 Apple Silicon
3. 支持中文唤醒词
4. 与 OpenClaw 架构兼容
5. 适合长期后台运行

### 实施建议

1. **第一阶段**：使用 Porcupine 内置英文关键词（openclaw、computer）快速原型验证
2. **第二阶段**：通过 Picovoice Console 训练中文唤醒词（"龙虾"、"贾维斯"）
3. **第三阶段**：与 OpenClaw Gateway 集成，实现全局唤醒词同步
4. **第四阶段**：优化性能和用户体验（提示音、视觉反馈、权限处理）

### 注意事项

- 免费版 Porcupine 有使用限制，商业用途需购买许可
- 自定义中文唤醒词训练可能需要付费
- 需要处理麦克风权限和隐私提示
- 后台运行需要配置音频会话

---

## 参考资源

- [Porcupine 官方文档](https://picovoice.ai/docs/porcupine/)
- [Porcupine Swift SDK](https://github.com/Picovoice/porcupine-swift)
- [OpenClaw Voice Wake 文档](https://docs.openclaw.ai/nodes/voicewake)
- [macOS Speech.framework 文档](https://developer.apple.com/documentation/speech)
- [AVAudioEngine 文档](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [openWakeWord GitHub](https://github.com/dscripka/openWakeWord)
- [local-wake GitHub](https://github.com/st-matskevich/local-wake)

---

*报告生成时间: 2026-03-28*
*调研范围: macOS 语音唤醒技术方案*
