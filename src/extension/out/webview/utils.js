"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getNonce = getNonce;
exports.formatDate = formatDate;
exports.getThemeColors = getThemeColors;
exports.createElement = createElement;
exports.sanitizeHtml = sanitizeHtml;
exports.generateUUID = generateUUID;
/**
 * Generate a nonce string
 * @returns A random nonce string
 */
function getNonce() {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
/**
 * Format a date string to a human-readable format
 * @param date ISO date string
 * @returns Formatted date string
 */
function formatDate(date) {
    return new Date(date).toLocaleString();
}
/**
 * Get the VS Code theme's color variables
 * @returns Object containing theme color variables
 */
function getThemeColors() {
    const computedStyle = window.getComputedStyle(document.documentElement);
    return {
        background: computedStyle.getPropertyValue('--vscode-editor-background'),
        foreground: computedStyle.getPropertyValue('--vscode-foreground'),
        border: computedStyle.getPropertyValue('--vscode-panel-border'),
        buttonBackground: computedStyle.getPropertyValue('--vscode-button-background'),
        buttonForeground: computedStyle.getPropertyValue('--vscode-button-foreground'),
        buttonHoverBackground: computedStyle.getPropertyValue('--vscode-button-hoverBackground'),
        successForeground: computedStyle.getPropertyValue('--vscode-testing-iconPassed'),
        errorForeground: computedStyle.getPropertyValue('--vscode-testing-iconFailed')
    };
}
/**
 * Create an element with attributes and children
 * @param tag HTML tag name
 * @param attributes Object containing element attributes
 * @param children Array of child elements or text content
 * @returns Created HTML element
 */
function createElement(tag, attributes = {}, children = []) {
    const element = document.createElement(tag);
    // Set attributes
    Object.entries(attributes).forEach(([key, value]) => {
        element.setAttribute(key, value);
    });
    // Add children
    children.forEach(child => {
        if (typeof child === 'string') {
            element.appendChild(document.createTextNode(child));
        }
        else {
            element.appendChild(child);
        }
    });
    return element;
}
/**
 * Sanitize HTML string to prevent XSS
 * @param html HTML string to sanitize
 * @returns Sanitized HTML string
 */
function sanitizeHtml(html) {
    const div = document.createElement('div');
    div.textContent = html;
    return div.innerHTML;
}
/**
 * Generate a UUID v4
 * @returns UUID string
 */
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}
//# sourceMappingURL=utils.js.map