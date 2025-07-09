import { createCanvas } from 'canvas';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Generate test images for E2E tests
 * This creates simple colored rectangles as placeholder images
 */
function generateTestImages() {
  const outputDir = path.join(__dirname, '../fixtures/images');
  
  // Ensure directory exists
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Generate regular test images
  const testImages = [
    { name: 'test-image-1.jpg', width: 800, height: 600, color: '#FF6B6B' },
    { name: 'test-image-2.jpg', width: 1024, height: 768, color: '#4ECDC4' },
    { name: 'test-image-3.jpg', width: 640, height: 480, color: '#45B7D1' },
  ];

  testImages.forEach(({ name, width, height, color }) => {
    const canvas = createCanvas(width, height);
    const ctx = canvas.getContext('2d');
    
    // Fill with color
    ctx.fillStyle = color;
    ctx.fillRect(0, 0, width, height);
    
    // Add some text
    ctx.fillStyle = 'white';
    ctx.font = '30px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(name, width / 2, height / 2);
    
    // Save as JPEG
    const buffer = canvas.toBuffer('image/jpeg');
    fs.writeFileSync(path.join(outputDir, name), buffer);
    console.log(`Generated ${name}`);
  });

  // Generate a large image (> 10MB)
  const largeCanvas = createCanvas(4000, 3000);
  const largeCtx = largeCanvas.getContext('2d');
  largeCtx.fillStyle = '#FF6B6B';
  largeCtx.fillRect(0, 0, 4000, 3000);
  
  // Add noise to increase file size
  const imageData = largeCtx.getImageData(0, 0, 4000, 3000);
  for (let i = 0; i < imageData.data.length; i += 4) {
    imageData.data[i] += Math.random() * 50; // R
    imageData.data[i + 1] += Math.random() * 50; // G
    imageData.data[i + 2] += Math.random() * 50; // B
  }
  largeCtx.putImageData(imageData, 0, 0);
  
  const largeBuffer = largeCanvas.toBuffer('image/jpeg', { quality: 1 });
  fs.writeFileSync(path.join(outputDir, 'large-image.jpg'), largeBuffer);
  console.log('Generated large-image.jpg');

  // Generate an invalid text file
  fs.writeFileSync(
    path.join(outputDir, 'invalid-file.txt'),
    'This is not an image file'
  );
  console.log('Generated invalid-file.txt');
}

// Run if called directly
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  generateTestImages();
}