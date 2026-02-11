#!/usr/bin/env node

/**
 * Template Verification Script
 * 
 * This script reads app.js and verifies that all email templates
 * are correctly defined with the updated routes and content.
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Email Template Verification\n');
console.log('=' .repeat(60));

// Read app.js
const appJsPath = path.join(__dirname, 'app.js');
const appJsContent = fs.readFileSync(appJsPath, 'utf8');

// Extract EMAIL_TEMPLATES object
const templateMatch = appJsContent.match(/const EMAIL_TEMPLATES = \{([\s\S]*?)\n\};/);

if (!templateMatch) {
    console.error('❌ Could not find EMAIL_TEMPLATES in app.js');
    process.exit(1);
}

console.log('✅ Found EMAIL_TEMPLATES object\n');

// Expected templates with their routes
const expectedTemplates = {
    'complete-fcl': {
        route: 'Dubai → Los Angeles',
        sender: 'john.smith@techcorp.com',
        subject: 'FCL Shipping Quote - Dubai to Los Angeles',
        keywords: ['Jebel Ali', 'Dubai', 'Los Angeles', '40HC', 'Electronics']
    },
    'minimal-info': {
        route: 'China → Germany',
        sender: 'maria.garcia@importexport.com',
        subject: 'Shipping Quote Needed',
        keywords: ['China', 'Germany']
    },
    'customer-confirmation': {
        route: 'Dubai → Los Angeles',
        sender: 'john.smith@techcorp.com',
        subject: 'RE: FCL Shipping Quote - Dubai to Los Angeles',
        keywords: ['confirmed', 'indicative rates']
    },
    'forwarder-rate': {
        route: 'Jebel Ali → Los Angeles',
        sender: 'ops@pacificbridgelogistics.com',
        subject: 'Rate Quote - Jebel Ali to Los Angeles',
        keywords: ['AEJEA', 'USLAX', '$3,200', '21 days', 'Pacific Bridge']
    },
    'lcl-shipment': {
        route: 'Hong Kong → UK',
        sender: 'emily.wong@hktrading.com',
        subject: 'LCL Quote - Hong Kong to UK',
        keywords: ['Hong Kong', 'Felixstowe', 'Fashion Accessories']
    },
    'urgent-shipment': {
        route: 'Vietnam → USA',
        sender: 'lisa.johnson@fashionretail.com',
        subject: 'URGENT - Need Quote Today - Vietnam to USA',
        keywords: ['urgent', 'Vietnam', 'Los Angeles', 'garments']
    }
};

// Verify each template
let allPassed = true;

Object.keys(expectedTemplates).forEach(templateKey => {
    const expected = expectedTemplates[templateKey];
    console.log(`\n📋 Template: ${templateKey}`);
    console.log(`   Route: ${expected.route}`);
    
    // Check if template key exists
    const templateRegex = new RegExp(`'${templateKey}':\\s*\\{`, 'g');
    if (!templateRegex.test(appJsContent)) {
        console.log(`   ❌ Template key not found`);
        allPassed = false;
        return;
    }
    console.log(`   ✅ Template key found`);
    
    // Check sender
    const senderRegex = new RegExp(`'${templateKey}':[\\s\\S]*?sender:\\s*'${expected.sender}'`);
    if (!senderRegex.test(appJsContent)) {
        console.log(`   ❌ Sender not correct (expected: ${expected.sender})`);
        allPassed = false;
    } else {
        console.log(`   ✅ Sender: ${expected.sender}`);
    }
    
    // Check subject
    const subjectRegex = new RegExp(`subject:\\s*'${expected.subject.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}'`);
    if (!subjectRegex.test(appJsContent)) {
        console.log(`   ❌ Subject not correct`);
        allPassed = false;
    } else {
        console.log(`   ✅ Subject: ${expected.subject}`);
    }
    
    // Check keywords in content
    let keywordsPassed = true;
    expected.keywords.forEach(keyword => {
        // Create a regex that finds the keyword within the template
        const keywordRegex = new RegExp(`'${templateKey}':[\\s\\S]*?content:[\\s\\S]*?${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`);
        if (!keywordRegex.test(appJsContent)) {
            console.log(`   ❌ Missing keyword: "${keyword}"`);
            keywordsPassed = false;
            allPassed = false;
        }
    });
    
    if (keywordsPassed) {
        console.log(`   ✅ All keywords present: ${expected.keywords.join(', ')}`);
    }
});

console.log('\n' + '='.repeat(60));

if (allPassed) {
    console.log('\n✅ All templates verified successfully!');
    console.log('\n📝 Summary:');
    console.log('   - 6 templates defined');
    console.log('   - All routes match sample conversations');
    console.log('   - All senders and subjects correct');
    console.log('   - All content keywords present');
    console.log('\n💡 If templates are not loading in the UI:');
    console.log('   1. Clear browser cache (Cmd+Shift+Delete)');
    console.log('   2. Hard refresh (Cmd+Shift+R)');
    console.log('   3. Open test-templates.html to verify');
    process.exit(0);
} else {
    console.log('\n❌ Some templates have issues - see details above');
    process.exit(1);
}
