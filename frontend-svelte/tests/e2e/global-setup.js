import { chromium } from '@playwright/test';
import { config } from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';

// Load environment variables from root .env file
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const envPath = join(__dirname, '../../../.env');

if (fs.existsSync(envPath)) {
  config({ path: envPath });
  console.log('Loaded environment variables from:', envPath);
}

async function globalSetup() {
  // Check for required environment variables
  const requiredEnvVars = ['API_KEY'];
  const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);
  
  if (missingVars.length > 0) {
    console.error('Missing required environment variables:', missingVars);
    console.error('Please ensure your .env file contains these variables');
    process.exit(1);
  }

  // Create a browser context to save authentication state
  const browser = await chromium.launch();
  const context = await browser.newContext();
  
  // Set up any global state or authentication here
  // For now, we'll just ensure the API key is available
  
  await browser.close();
  
  // Return configuration that will be available to all tests
  return {
    apiKey: process.env.API_KEY,
    baseURL: process.env.FRONTEND_URL || 'http://localhost:3000',
    apiURL: process.env.API_URL || 'http://localhost:8000',
  };
}

export default globalSetup;