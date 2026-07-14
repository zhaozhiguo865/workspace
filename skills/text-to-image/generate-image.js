#!/usr/bin/env node
/**
 * 文字生图工具 - 使用 DALL-E 3 API
 * Usage: node generate-image.js "prompt" [--size=1024x1024] [--output=image.png]
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// 配置
const API_KEY = process.env.OPENAI_API_KEY;
const API_HOST = 'api.openai.com';

// 解析参数
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    prompt: '',
    size: '1024x1024', // 1024x1024, 1792x1024, 1024x1792
    quality: 'standard', // standard, hd
    output: null,
    style: 'vivid' // vivid, natural
  };
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--size=')) {
      options.size = arg.replace('--size=', '');
    } else if (arg.startsWith('--quality=')) {
      options.quality = arg.replace('--quality=', '');
    } else if (arg.startsWith('--output=')) {
      options.output = arg.replace('--output=', '');
    } else if (arg.startsWith('--style=')) {
      options.style = arg.replace('--style=', '');
    } else if (!arg.startsWith('--')) {
      options.prompt = arg;
    }
  }
  
  return options;
}

// 生成图片
async function generateImage(options) {
  if (!API_KEY) {
    console.error('错误: 请设置 OPENAI_API_KEY 环境变量');
    process.exit(1);
  }
  
  if (!options.prompt) {
    console.error('用法: node generate-image.js "你的描述" [--size=1024x1024] [--output=image.png]');
    process.exit(1);
  }
  
  const data = JSON.stringify({
    model: 'dall-e-3',
    prompt: options.prompt,
    n: 1,
    size: options.size,
    quality: options.quality,
    style: options.style,
    response_format: 'url'
  });
  
  console.log('🎨 正在生成图片...');
  console.log(`提示词: ${options.prompt}`);
  console.log(`尺寸: ${options.size}`);
  console.log(`质量: ${options.quality}`);
  console.log('');
  
  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: API_HOST,
      path: '/v1/images/generations',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    }, (res) => {
      let responseData = '';
      res.on('data', chunk => responseData += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(responseData);
          if (result.error) {
            reject(new Error(result.error.message));
          } else {
            resolve(result.data[0]);
          }
        } catch (e) {
          reject(e);
        }
      });
    });
    
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

// 下载图片
async function downloadImage(url, outputPath) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(outputPath);
    https.get(url, (res) => {
      res.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve(outputPath);
      });
    }).on('error', reject);
  });
}

// 主函数
async function main() {
  const options = parseArgs();
  
  try {
    const result = await generateImage(options);
    
    console.log('✅ 图片生成成功!');
    console.log(`URL: ${result.url}`);
    console.log(`修订后提示词: ${result.revised_prompt}`);
    
    // 如果指定了输出路径，下载图片
    if (options.output) {
      const outputPath = path.resolve(options.output);
      await downloadImage(result.url, outputPath);
      console.log(`💾 图片已保存: ${outputPath}`);
    }
    
    // 输出 JSON 格式供其他工具使用
    console.log('\n📤 JSON 输出:');
    console.log(JSON.stringify({
      success: true,
      url: result.url,
      revised_prompt: result.revised_prompt,
      local_path: options.output || null
    }, null, 2));
    
  } catch (error) {
    console.error('❌ 生成失败:', error.message);
    process.exit(1);
  }
}

main();
