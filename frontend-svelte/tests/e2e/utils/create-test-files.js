import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Create minimal test files for E2E tests
 */
export function createTestFiles() {
  const outputDir = path.join(__dirname, '../fixtures/images');
  
  // Ensure directory exists
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Create a minimal valid JPEG header
  const jpegHeader = Buffer.from([
    0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46,
    0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01,
    0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43
  ]);

  // Create test images
  ['test-image-1.jpg', 'test-image-2.jpg', 'test-image-3.jpg'].forEach((filename) => {
    const filepath = path.join(outputDir, filename);
    if (!fs.existsSync(filepath)) {
      fs.writeFileSync(filepath, jpegHeader);
      console.log(`Created ${filename}`);
    }
  });

  // Create a larger file
  const largeFilePath = path.join(outputDir, 'large-image.jpg');
  if (!fs.existsSync(largeFilePath)) {
    const largeBuffer = Buffer.alloc(11 * 1024 * 1024); // 11MB
    jpegHeader.copy(largeBuffer);
    fs.writeFileSync(largeFilePath, largeBuffer);
    console.log('Created large-image.jpg');
  }

  // Create an invalid text file
  const invalidFilePath = path.join(outputDir, 'invalid-file.txt');
  if (!fs.existsSync(invalidFilePath)) {
    fs.writeFileSync(invalidFilePath, 'This is not an image file');
    console.log('Created invalid-file.txt');
  }

  return {
    testImage1: path.join(outputDir, 'test-image-1.jpg'),
    testImage2: path.join(outputDir, 'test-image-2.jpg'),
    testImage3: path.join(outputDir, 'test-image-3.jpg'),
    largeImage: path.join(outputDir, 'large-image.jpg'),
    invalidFile: path.join(outputDir, 'invalid-file.txt'),
  };
}