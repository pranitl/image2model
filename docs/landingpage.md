# PRD: Landing Page Redesign

**Version:** 1.0
**Date:** 2023-10-27
**Author:** AI Assistant

---

## 1. Overview

This document outlines the requirements for redesigning the application's landing page (`HomePage.tsx`). The goal is to transform the current light-themed, multi-section page into a sleek, modern, dark-themed page that aligns with the provided mockup. This redesign aims to improve user engagement and provide a more visually appealing and intuitive introduction to the product.

## 2. Background

The current landing page is functional but does not match the branding and aesthetic of the new design direction. The provided mockup (`ChatGPT Image Jul 2, 2025, 09_51_50 PM.png`) presents a more professional and compelling user experience. To improve user perception and conversion rates, the landing page must be updated to reflect this new design.

## 3. Goals

-   Implement a visually striking dark theme across the entire landing page.
-   Replicate the layout and styling of the provided mockup with pixel-perfect accuracy.
-   Restructure the "How It Works" section to be more engaging and informative.
-   Ensure all text content matches the mockup (with spelling corrections).
-   Improve the overall user experience and visual appeal of the page.

## 4. Requirements

### 4.1. General: Dark Theme Implementation

-   **Background:** The entire page should use a dark background, specifically a near-black or very dark navy color as seen in the mockup.
-   **Typography:** All text should be a light color (white or light gray) to ensure high contrast and readability against the dark background.
-   **Color Palette:** The primary accent color for buttons and highlights should be the vibrant purple/blue shown in the mockup.

### 4.2. Hero Section

-   **Layout:** A single-column, centered layout.
-   **Headline:**
    -   Text: "Transform Images into 3D Models"
    -   Styling: Large, bold, light-colored font.
-   **Sub-headline:**
    -   Text: "Harness the power of AI to convert your 2D images into stunning 3D models. Perfect for game development, 3D printing, and digital art projects."
    -   Styling: Smaller, regular-weight font below the main headline.
-   **Call-to-Action (CTA) Button:**
    -   Text: "Start Creating"
    -   Styling: Solid fill with the primary purple/blue accent color.
    -   Action: Navigates to the `/upload` page.
    -   **Note:** The secondary "Learn More" button from the current implementation should be removed.

### 4.3. "How It Works" Section

This section requires a significant layout overhaul from the current three-column grid.

-   **Layout:** A two-column layout. The left column will contain the stepper, and the right column will feature a product image.
-   **Left Column (Stepper):**
    -   **Title:** "How It Works"
    -   **Stepper Component:** A new vertical stepper component needs to be created.
        -   It should display three steps, visually connected by a line.
        -   The currently active step (e.g., Step 2 in the mockup) should be visually distinct (highlighted with the accent color).
    -   **Step 1:**
        -   Icon: Upload icon.
        -   Title: "Upload Images"
        -   Description: "Simply upload your images for our AI to analyze and generate 3D models."
    -   **Step 2:**
        -   Icon: Zap/Lightning icon.
        -   Title: "AI Processing"
        -   Description: "Our AI processes your images and generates detailed 3D models."
    -   **Step 3:**
        -   Icon: Download icon.
        -   Title: "Download Models"
        -   Description: "Download your 3D models and use them in your projects."
-   **Right Column (Image):**
    -   A large, high-quality image of a 3D model (human head) should be displayed, as shown in the mockup.

### 4.4. Call-to-Action (CTA) Section

-   **Layout:** A single-column, centered layout at the bottom of the page.
-   **Title:**
    -   Text: "Ready to Get Started?"
    -   Styling: Large, bold, light-colored font.
-   **Sub-headline:**
    -   Text: "Get started with your first 3D model today."
-   **CTA Button:**
    -   Text: "Upload Image"
    -   Styling: Solid fill with the primary purple/blue accent color.
    -   Action: Navigates to the `/upload` page.

### 4.5. Visual Assets

-   **Icons:** The icons for the "How It Works" section should be updated to match the style in the mockup. The current `lucide-react` icons have a different aesthetic.
-   **Product Image:** The 3D model image for the "How It Works" section needs to be sourced and integrated.

## 5. Non-Goals

-   Changes to other pages (e.g., Upload, Results).
-   Implementing the "Learn More" functionality (as the button is being removed).
-   Adding any new sections not present in the mockup.
-   Backend logic changes. This is a frontend-only task.

## 6. Technical Specifications

-   **Framework:** Continue using React and TypeScript.
-   **Styling:** Continue using Tailwind CSS. All new styles should be implemented using Tailwind utility classes.
-   **Component Structure:**
    -   The `HomePage.tsx` file will be heavily modified.
    -   A new reusable `Stepper` component should be created to handle the "How It Works" section's steps.
-   **Routing:** Continue using `react-router-dom` for navigation. No changes are expected for the routes themselves.
