// Application State
const state = {
    threadId: null,
    emailHistory: [],
    formState: {
        emailType: 'Customer',
        senderEmail: 'john.doe@techcorp.com',
        subject: 'FCL Shipping Quote - Shanghai to Los Angeles',
        content: ''
    },
    selectedTemplate: null,
    apiBaseUrl: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
        ? 'http://localhost:5001' 
        : 'http://localhost:5001'  // Change this if your API is on a different host/port
};

// Email Templates
const EMAIL_TEMPLATES = {
    'complete-fcl': {
        type: 'Customer',
        sender: 'john.doe@techcorp.com',
        subject: 'FCL Shipping Quote - Shanghai to Los Angeles',
        content: `Hello Searates,

I need a shipping quote for a full container load from Shanghai, China to Los Angeles, USA.

Details:
- Origin: Shanghai, China
- Destination: Los Angeles, USA
- Container Type: 40HC
- Number of Containers: 2
- Commodity: Electronics
- Weight: 20,000 kg per container
- Ready Date: 2024-03-15
- Incoterm: FOB

Please provide rates and transit time.

Best regards,
John Doe
Logistics Manager
TechCorp Inc.`
    },
    'minimal-info': {
        type: 'Customer',
        sender: 'sarah.williams@manufacturing.com',
        subject: 'Shipping Quote Request',
        content: `Hi,

I want to ship from USA to China.

Please send me a quote.

Thanks,
Sarah Williams`
    },
    'customer-confirmation': {
        type: 'Customer',
        sender: 'john.doe@techcorp.com',
        subject: 'Re: FCL Shipping Quote - Shanghai to Los Angeles',
        content: `Hi,

I confirm the details are correct. Please proceed with the booking.

Best regards,
John Doe`
    },
    'forwarder-rate': {
        type: 'Forwarder',
        sender: 'ops@pacificbridgelogistics.com',
        subject: 'Rate Quote - Shanghai to Los Angeles',
        content: `Dear Logistics Team,

Please find our rate quote:

Route: Shanghai (CNSHG) to Los Angeles (USLAX)
Container: 40HC
Rate: $2,850 USD
Transit Time: 18 days
Valid Until: December 31, 2024

Please confirm if you would like to proceed.

Best regards,
Pacific Bridge Logistics`
    },
    'lcl-shipment': {
        type: 'Customer',
        sender: 'mike.chen@trading.com',
        subject: 'LCL Shipping Quote Request',
        content: `Dear SeaRates Team,

I need a quote for LCL shipment:

- Origin: Singapore
- Destination: New York, USA
- Weight: 500 kg
- Volume: 2.5 CBM
- Commodity: Textiles
- Ready Date: 2024-04-01

Please provide your best rates.

Best regards,
Mike Chen
Trading Co.`
    }
};

// Initialize Application
function init() {
    console.log('🚀 Initializing application...');
    loadState();
    setupEventListeners();
    updateUI();
    console.log('✅ Application initialized');
    console.log('📊 Initial state:', { threadId: state.threadId, historyCount: state.emailHistory.length });
}

// Load state from localStorage
function loadState() {
    const savedThreadId = localStorage.getItem('threadId');
    const savedHistory = localStorage.getItem('emailHistory');
    
    if (savedThreadId) {
        state.threadId = savedThreadId;
    } else {
        generateThreadId();
    }
    
    if (savedHistory) {
        try {
            state.emailHistory = JSON.parse(savedHistory);
        } catch (e) {
            console.error('Error loading history:', e);
            state.emailHistory = [];
        }
    }
}

// Save state to localStorage (optimized - non-blocking)
function saveState() {
    // Use try-catch to prevent blocking on localStorage errors
    try {
        // Defer localStorage write to avoid blocking UI
        setTimeout(() => {
            localStorage.setItem('threadId', state.threadId);
            localStorage.setItem('emailHistory', JSON.stringify(state.emailHistory));
        }, 0);
    } catch (e) {
        console.warn('⚠️ Failed to save state to localStorage:', e);
    }
}

// Get current time in Abu Dhabi timezone (UTC+4)
function getAbuDhabiTime() {
    const now = new Date();
    // Abu Dhabi is UTC+4
    const abuDhabiOffset = 4 * 60; // 4 hours in minutes
    const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
    const abuDhabiTime = new Date(utc + (abuDhabiOffset * 60000));
    return abuDhabiTime;
}

// Format timestamp in Abu Dhabi timezone
function formatAbuDhabiTimestamp() {
    const abuDhabiTime = getAbuDhabiTime();
    const year = abuDhabiTime.getFullYear();
    const month = String(abuDhabiTime.getMonth() + 1).padStart(2, '0');
    const day = String(abuDhabiTime.getDate()).padStart(2, '0');
    const hours = String(abuDhabiTime.getHours()).padStart(2, '0');
    const minutes = String(abuDhabiTime.getMinutes()).padStart(2, '0');
    const seconds = String(abuDhabiTime.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

// Generate new thread ID
function generateThreadId() {
    const abuDhabiTime = getAbuDhabiTime();
    const timestamp = abuDhabiTime.toISOString()
        .replace(/[-:]/g, '')
        .replace(/\..+/, '')
        .replace('T', '_');
    state.threadId = `demo_thread_${timestamp}`;
    saveState();
}

// Setup event listeners
function setupEventListeners() {
    console.log('🔗 Setting up event listeners...');
    
    // Thread reset
    const resetBtn = document.getElementById('reset-thread-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetThread);
        console.log('✅ Reset thread button listener added');
    } else {
        console.error('❌ Reset thread button not found');
    }
    
    // Template selector
    const templateSelector = document.getElementById('template-selector');
    if (templateSelector) {
        templateSelector.addEventListener('change', handleTemplateSelect);
        console.log('✅ Template selector listener added');
    } else {
        console.error('❌ Template selector not found');
    }
    
    // Email type change
    const emailType = document.getElementById('email-type');
    if (emailType) {
        emailType.addEventListener('change', handleEmailTypeChange);
        console.log('✅ Email type listener added');
    } else {
        console.error('❌ Email type selector not found');
    }
    
    // Email form submission
    const emailForm = document.getElementById('email-form');
    if (emailForm) {
        emailForm.addEventListener('submit', handleEmailSubmit);
        console.log('✅ Email form submit listener added');
    } else {
        console.error('❌ Email form not found');
    }
    
    // Sidebar toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
        console.log('✅ Sidebar toggle listener added');
    }
    
    const sidebarClose = document.getElementById('sidebar-close');
    if (sidebarClose) {
        sidebarClose.addEventListener('click', toggleSidebar);
        console.log('✅ Sidebar close listener added');
    }
    
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', toggleSidebar);
        console.log('✅ Sidebar overlay listener added');
    }
    
    console.log('✅ All event listeners set up');
}

// Update UI based on state
function updateUI() {
    // Update thread ID display
    document.getElementById('thread-id').textContent = state.threadId;
    
    // Update form fields
    document.getElementById('email-type').value = state.formState.emailType;
    document.getElementById('sender-email').value = state.formState.senderEmail;
    document.getElementById('subject').value = state.formState.subject;
    document.getElementById('content').value = state.formState.content;
    
    // Update sender email label
    updateSenderEmailLabel();
    
    // Update history
    updateHistoryDisplay();
}

// Update sender email label based on type
function updateSenderEmailLabel() {
    const label = document.getElementById('sender-email-label');
    const type = state.formState.emailType;
    label.textContent = type === 'Customer' ? 'Customer Email' : 'Forwarder Email';
}

// Handle email type change
function handleEmailTypeChange(e) {
    state.formState.emailType = e.target.value;
    updateSenderEmailLabel();
}

// Show status indicator
function showStatus(icon, text) {
    const indicator = document.getElementById('status-indicator');
    const statusIcon = document.getElementById('status-icon');
    const statusText = document.getElementById('status-text');
    
    if (indicator && statusIcon && statusText) {
        statusIcon.textContent = icon;
        statusText.textContent = text;
        indicator.style.display = 'block';
    }
    console.log(`${icon} ${text}`);
}

function hideStatus() {
    const indicator = document.getElementById('status-indicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
}

// Handle template selection
function handleTemplateSelect(e) {
    const templateKey = e.target.value;
    if (!templateKey) return;
    
    const template = EMAIL_TEMPLATES[templateKey];
    if (!template) return;
    
    // Update form state
    state.formState.emailType = template.type;
    state.formState.senderEmail = template.sender;
    state.formState.subject = template.subject;
    state.formState.content = template.content;
    state.selectedTemplate = templateKey;
    
    // Update UI
    updateUI();
    
    // Show success message
    const messageDiv = document.getElementById('template-message');
    messageDiv.textContent = `✅ Loaded template: ${e.target.options[e.target.selectedIndex].text}`;
    messageDiv.style.display = 'block';
    
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 3000);
}

// Handle email form submission
async function handleEmailSubmit(e) {
    e.preventDefault();
    
    console.log('📧 Form submitted - handleEmailSubmit called');
    
    // Immediate visual feedback - button clicked!
    const processBtn = document.getElementById('process-btn');
    const processBtnText = document.getElementById('process-btn-text');
    const processBtnSpinner = document.getElementById('process-btn-spinner');
    
    if (processBtn) {
        processBtn.disabled = true;
        processBtn.style.opacity = '0.7';
    }
    if (processBtnText) processBtnText.style.display = 'none';
    if (processBtnSpinner) processBtnSpinner.style.display = 'inline';
    
    showStatus('✅', 'Button clicked! Validating form...');
    
    const sender = document.getElementById('sender-email').value.trim();
    const subject = document.getElementById('subject').value.trim();
    const content = document.getElementById('content').value.trim();
    const emailType = document.getElementById('email-type').value;
    
    console.log('📝 Form data:', { sender, subject, content: content.substring(0, 50) + '...', emailType });
    
    if (!content) {
        showStatus('❌', 'Error: Email content cannot be empty');
        if (processBtn) processBtn.disabled = false;
        if (processBtnText) processBtnText.style.display = 'inline';
        if (processBtnSpinner) processBtnSpinner.style.display = 'none';
        showMessage('❌ Email content cannot be empty', 'error');
        setTimeout(hideStatus, 3000);
        return;
    }
    
    // Show loading and status
    showLoading(true);
    showStatus('⏳', 'Form validated. Calling API...');
    hideResponse();
    
    // Scroll to top to show loading spinner
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    console.log('🌐 Calling API:', `${state.apiBaseUrl}/api/process-email`);
    
    try {
        showStatus('🌐', 'API request sent. Waiting for response...');
        
        const startTime = Date.now();
        const response = await fetch(`${state.apiBaseUrl}/api/process-email`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sender: sender,
                subject: subject,
                content: content,
                thread_id: state.threadId
            })
        });
        
        const responseTime = Date.now() - startTime;
        console.log(`⏱️ API response received in ${responseTime}ms`);
        
        if (!response.ok) {
            showStatus('❌', `API Error: HTTP ${response.status}`);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        showStatus('📥', 'Response received. Processing...');
        const data = await response.json();
        
        console.log('✅ API Response received:', { 
            success: data.success, 
            thread_id: data.thread_id 
        });
        
        if (!data.success) {
            showStatus('❌', `Error: ${data.error || 'Unknown error'}`);
            throw new Error(data.error || 'Unknown error occurred');
        }
        
        showStatus('✅', 'Processing workflow response...');
        
        // Update thread ID if changed
        if (data.thread_id && data.thread_id !== state.threadId) {
            state.threadId = data.thread_id;
            saveState();
        }
        
        // Process response immediately (optimized for speed)
        processWorkflowResponse(data, emailType, sender, subject, content, processBtn, processBtnText, processBtnSpinner);
        
        // Update form state (non-blocking)
        state.formState.senderEmail = sender;
        state.formState.subject = subject;
        state.formState.content = content;
        
    } catch (error) {
        console.error('❌ Error processing email:', error);
        console.error('Error details:', {
            message: error.message,
            stack: error.stack,
            apiUrl: `${state.apiBaseUrl}/api/process-email`
        });
        
        showStatus('❌', `Error: ${error.message}`);
        showMessage(`❌ Error processing email: ${error.message}`, 'error');
        
        // Reset button state on error
        if (processBtn) {
            processBtn.disabled = false;
            processBtn.style.opacity = '1';
        }
        if (processBtnText) processBtnText.style.display = 'inline';
        if (processBtnSpinner) processBtnSpinner.style.display = 'none';
        
        // Hide status after 5 seconds on error
        setTimeout(() => {
            hideStatus();
        }, 5000);
    } finally {
        showLoading(false);
    }
}

// Process workflow response
function processWorkflowResponse(data, emailType, sender, subject, content, processBtn = null, processBtnText = null, processBtnSpinner = null) {
    const workflowState = data.result;
    
    // Find response (priority order)
    let response = null;
    let responseType = null;
    
    if (workflowState.confirmation_response_result && !workflowState.confirmation_response_result.error) {
        response = workflowState.confirmation_response_result;
        responseType = 'Confirmation Request';
    } else if (workflowState.clarification_response_result && !workflowState.clarification_response_result.error) {
        response = workflowState.clarification_response_result;
        responseType = 'Clarification Request';
    } else if (workflowState.confirmation_acknowledgment_result && !workflowState.confirmation_acknowledgment_result.error) {
        response = workflowState.confirmation_acknowledgment_result;
        responseType = 'Confirmation Acknowledgment';
    } else if (workflowState.acknowledgment_response_result && !workflowState.acknowledgment_response_result.error) {
        response = workflowState.acknowledgment_response_result;
        const senderType = response.sender_type || '';
        responseType = senderType === 'forwarder' ? 'Forwarder Acknowledgment' : 'Acknowledgment';
    }
    
    // Extract additional data
    const forwarderAssignment = workflowState.forwarder_assignment_result;
    const forwarderResponse = workflowState.forwarder_response_result;
    const salesNotification = workflowState.sales_notification_result;
    const customerQuote = workflowState.customer_quote_result;
    
    // Create history entry
    const historyEntry = {
        timestamp: formatAbuDhabiTimestamp(),
        type: emailType,
        sender: sender,
        subject: subject,
        content: content,
        response: response,
        responseType: responseType,
        forwarderAssignment: forwarderAssignment,
        forwarderResponse: forwarderResponse,
        salesNotification: salesNotification,
        customerQuote: customerQuote,
        workflowState: workflowState
    };
    
    // Add to history
    state.emailHistory.push(historyEntry);
    
    // Display response IMMEDIATELY (optimized - show first, update history later)
    showStatus('📤', 'Displaying response...');
    displayResponse(response, responseType, forwarderAssignment, forwarderResponse, 
                    salesNotification, customerQuote, workflowState, emailType);
    
    // Display agent performance in sidebar
    displayAgentPerformance(workflowState);
    
    // Hide loading immediately after displaying response
    showLoading(false);
    showStatus('✅', 'Response displayed successfully!');
    
    // Reset button state
    if (processBtn) {
        processBtn.disabled = false;
        processBtn.style.opacity = '1';
    }
    if (processBtnText) processBtnText.style.display = 'inline';
    if (processBtnSpinner) processBtnSpinner.style.display = 'none';
    
    // Show success message immediately
    showMessage('✅ Email processed successfully!', 'success');
    
    // Hide status after 3 seconds
    setTimeout(() => {
        hideStatus();
    }, 3000);
    
    // Defer heavy operations to avoid blocking UI
    requestAnimationFrame(() => {
        // Save state (non-blocking)
        saveState();
        // Update history display (non-blocking)
        updateHistoryDisplay();
    });
}

// Display response (optimized for speed)
function displayResponse(response, responseType, forwarderAssignment, forwarderResponse,
                        salesNotification, customerQuote, workflowState, emailType) {
    // Show response section immediately
    const responseSection = document.getElementById('response-section');
    responseSection.style.display = 'block';
    responseSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Use DocumentFragment for faster DOM updates
    const fragment = document.createDocumentFragment();
    
    // Main response
    const mainResponse = document.getElementById('main-response');
    if (response && !response.error) {
        mainResponse.style.display = 'block';
        mainResponse.innerHTML = `
            <h3>✅ Response Generated (${responseType})</h3>
            <div class="response-field">
                <strong>Subject:</strong>
                <div>${response.subject || 'N/A'}</div>
            </div>
            <div class="response-field">
                <strong>Body:</strong>
                <div class="response-body">${escapeHtml(response.body || 'N/A')}</div>
            </div>
        `;
    } else {
        mainResponse.innerHTML = `
            <h3>⚠️ No Response Generated</h3>
            <p>No valid response was found in the workflow state.</p>
        `;
    }
    
    // Forwarder Assignment
    if (forwarderAssignment) {
        const forwarderDiv = document.getElementById('forwarder-assignment');
        forwarderDiv.style.display = 'block';
        const assignedForwarder = forwarderAssignment.assigned_forwarder || {};
        const rateRequest = forwarderAssignment.rate_request || {};
        
        forwarderDiv.innerHTML = `
            <h3>🚚 Forwarder Assignment</h3>
            <div class="two-columns">
                <div>
                    <h4>Forwarder Details:</h4>
                    <p><strong>Name:</strong> ${assignedForwarder.name || 'N/A'}</p>
                    <p><strong>Email:</strong> ${assignedForwarder.email || 'N/A'}</p>
                    <p><strong>Company:</strong> ${assignedForwarder.company || 'N/A'}</p>
                </div>
                <div>
                    <h4>Rate Request Email:</h4>
                    <p><strong>To:</strong> ${rateRequest.to_email || 'N/A'}</p>
                    <p><strong>Subject:</strong> ${rateRequest.subject || 'N/A'}</p>
                    <p><strong>Body:</strong></p>
                    <div class="response-body">${escapeHtml(rateRequest.body || 'N/A')}</div>
                </div>
            </div>
        `;
        
        // Auto-populate main form for forwarder response
        const forwarderEmail = assignedForwarder.email;
        const forwarderName = assignedForwarder.name || 'Forwarder Team';
        const forwarderCompany = assignedForwarder.company || '';
        
        if (forwarderEmail) {
            // Switch email type to Forwarder
            const emailTypeSelect = document.getElementById('email-type');
            if (emailTypeSelect) {
                emailTypeSelect.value = 'Forwarder';
                state.formState.emailType = 'Forwarder';
            }
            
            // Pre-fill forwarder email
            const senderEmailInput = document.getElementById('sender-email');
            if (senderEmailInput) {
                senderEmailInput.value = forwarderEmail;
                state.formState.senderEmail = forwarderEmail;
            }
            
            // Update sender email label
            updateSenderEmailLabel();
            
            // Pre-fill subject with default if empty
            const subjectInput = document.getElementById('subject');
            if (subjectInput && !subjectInput.value.trim()) {
                const origin = forwarderAssignment.origin_country || '';
                const dest = forwarderAssignment.destination_country || '';
                const defaultSubject = origin && dest 
                    ? `Rate Quote - ${origin} to ${dest}`
                    : 'Rate Quote - Shipping Request';
                subjectInput.value = defaultSubject;
            }
            
            // Pre-fill default email body for forwarder
            const contentTextarea = document.getElementById('content');
            if (contentTextarea && !contentTextarea.value.trim()) {
                const originPort = forwarderAssignment.origin_country || 'Origin';
                const destPort = forwarderAssignment.destination_country || 'Destination';
                const containerType = forwarderAssignment.container_type || '40HC';
                const validUntil = new Date();
                validUntil.setMonth(validUntil.getMonth() + 1);
                const validUntilStr = validUntil.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
                
                const defaultBody = `Dear Logistics Team,

Please find our rate quote:

Route: ${originPort} to ${destPort}
Container: ${containerType}
Rate: $2,850 USD
Transit Time: 18 days
Valid Until: ${validUntilStr}

Rate provided as requested. Please confirm if you would like to proceed.

Best regards,
${forwarderName}${forwarderCompany ? '\n' + forwarderCompany : ''}`;
                
                contentTextarea.value = defaultBody;
                state.formState.content = defaultBody;
            }
            
            // Show info message
            showMessage('✅ Forwarder assigned! You can now send email as forwarder using the form above.', 'info');
            
            // Scroll to form after a short delay to ensure UI is updated
            setTimeout(() => {
                const emailFormSection = document.querySelector('.email-form-section');
                if (emailFormSection) {
                    emailFormSection.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'start' 
                    });
                }
            }, 500);
        }
    }
    
    // Forwarder Response (Rates)
    if (forwarderResponse && !forwarderResponse.error) {
        const forwarderRespDiv = document.getElementById('forwarder-response');
        forwarderRespDiv.style.display = 'block';
        const rateInfo = forwarderResponse.rate_info || {};
        
        forwarderRespDiv.innerHTML = `
            <h3>📊 Forwarder Response (Rates Received)</h3>
            <div class="two-columns">
                <div>
                    <h4>Rate Information:</h4>
                    <p><strong>Rate:</strong> ${rateInfo.rate || 'N/A'}</p>
                    <p><strong>Currency:</strong> ${rateInfo.currency || 'N/A'}</p>
                    <p><strong>Transit Time:</strong> ${rateInfo.transit_time || 'N/A'}</p>
                </div>
                <div>
                    <h4>Additional Details:</h4>
                    <p><strong>Valid Until:</strong> ${rateInfo.valid_until || 'N/A'}</p>
                    <p><strong>Sailing Date:</strong> ${rateInfo.sailing_date || 'N/A'}</p>
                    ${rateInfo.additional_notes ? `<p><strong>Notes:</strong> ${rateInfo.additional_notes}</p>` : ''}
                </div>
            </div>
        `;
    }
    
    // Sales Notification
    if (salesNotification && !salesNotification.error) {
        const salesDiv = document.getElementById('sales-notification');
        salesDiv.style.display = 'block';
        salesDiv.innerHTML = `
            <h3>📧 Sales Notification (Collated Email)</h3>
            <p class="message message-info">This email contains customer requirements and forwarder rate information for the sales team.</p>
            <div class="response-field">
                <strong>Subject:</strong> ${salesNotification.subject || 'N/A'}
            </div>
            <div class="response-field">
                <strong>To:</strong> ${salesNotification.to || 'Sales Team'}
            </div>
            <div class="response-field">
                <strong>Priority:</strong> ${salesNotification.priority || 'N/A'}
            </div>
            <div class="response-field">
                <strong>Body:</strong>
                <div class="response-body">${escapeHtml(salesNotification.body || 'N/A')}</div>
            </div>
        `;
    }
    
    // Customer Quote
    if (customerQuote && !customerQuote.error) {
        const quoteDiv = document.getElementById('customer-quote');
        quoteDiv.style.display = 'block';
        quoteDiv.innerHTML = `
            <h3>📨 Final Customer Quote Email</h3>
            <p class="message message-success">This is the final email to be sent to the customer with rates.</p>
            <div class="response-field">
                <strong>Subject:</strong> ${customerQuote.subject || 'N/A'}
            </div>
            <div class="response-field">
                <strong>To:</strong> ${customerQuote.to || 'N/A'}
            </div>
            <div class="response-field">
                <strong>From:</strong> ${customerQuote.from || 'N/A'}
            </div>
            <div class="response-field">
                <strong>Body:</strong>
                <div class="response-body">${escapeHtml(customerQuote.body || 'N/A')}</div>
            </div>
        `;
    }
    
    // Forwarder Acknowledgment - Only show if NOT a forwarder email (to avoid duplication)
    // Forwarder emails are handled by displayForwarderResponses() function
    if (workflowState.acknowledgment_response_result && emailType !== 'Forwarder') {
        const ack = workflowState.acknowledgment_response_result;
        if (ack.sender_type === 'forwarder' && !ack.error) {
            const ackDiv = document.getElementById('forwarder-acknowledgment');
            ackDiv.style.display = 'block';
            ackDiv.innerHTML = `
                <h3>🤝 Forwarder Acknowledgment</h3>
                <p class="message message-info">Bot's response to forwarder email.</p>
                <div class="response-field">
                    <strong>Subject:</strong> ${ack.subject || 'N/A'}
                </div>
                <div class="response-field">
                    <strong>To:</strong> ${ack.sender_email || 'N/A'}
                </div>
                <div class="response-field">
                    <strong>Body:</strong>
                    <div class="response-body">${escapeHtml(ack.body || 'N/A')}</div>
                </div>
            `;
        }
    }
    
    // Debug section (if no response or errors)
    if (!response || response.error) {
        const debugDiv = document.getElementById('debug-section');
        debugDiv.style.display = 'block';
        debugDiv.innerHTML = `
            <h3>🔍 Debug: Workflow State</h3>
            <pre>${JSON.stringify(workflowState, null, 2)}</pre>
        `;
    }
}

// Display forwarder-specific responses (acknowledgment + sales notification) - optimized
function displayForwarderResponses(forwarderAcknowledgment, salesNotification) {
    // Show response section immediately and scroll to it
    const responseSection = document.getElementById('response-section');
    responseSection.style.display = 'block';
    responseSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Clear main response section (not used for forwarder responses)
    const mainResponse = document.getElementById('main-response');
    mainResponse.style.display = 'none';
    mainResponse.innerHTML = '';
    
    // Display Forwarder Acknowledgment (Response 1)
    if (forwarderAcknowledgment && !forwarderAcknowledgment.error) {
        const ackDiv = document.getElementById('forwarder-acknowledgment');
        ackDiv.style.display = 'block';
        ackDiv.innerHTML = `
            <h3>🤝 Forwarder Acknowledgment</h3>
            <p class="message message-info">Bot's response to forwarder email.</p>
            <div class="response-field">
                <strong>Subject:</strong> ${forwarderAcknowledgment.subject || 'N/A'}
            </div>
            <div class="response-field">
                <strong>To:</strong> ${forwarderAcknowledgment.sender_email || forwarderAcknowledgment.to || 'N/A'}
            </div>
            <div class="response-field">
                <strong>Body:</strong>
                <div class="response-body">${escapeHtml(forwarderAcknowledgment.body || 'N/A')}</div>
            </div>
        `;
        console.log('✅ Forwarder acknowledgment displayed');
    } else {
        const ackDiv = document.getElementById('forwarder-acknowledgment');
        ackDiv.style.display = 'none';
        console.log('⚠️ No forwarder acknowledgment to display');
    }
    
    // Display Sales Notification (Response 2)
    if (salesNotification && !salesNotification.error) {
        const salesDiv = document.getElementById('sales-notification');
        salesDiv.style.display = 'block';
        salesDiv.innerHTML = `
            <h3>📧 Sales Notification (Collated Email)</h3>
            <p class="message message-info">This email contains customer requirements and forwarder rate information for the sales team.</p>
            <div class="response-field">
                <strong>Subject:</strong> ${salesNotification.subject || 'N/A'}
            </div>
            <div class="response-field">
                <strong>To:</strong> ${salesNotification.to || 'Sales Team'}
            </div>
            <div class="response-field">
                <strong>Priority:</strong> ${salesNotification.priority || 'N/A'}
            </div>
            <div class="response-field">
                <strong>Body:</strong>
                <div class="response-body">${escapeHtml(salesNotification.body || 'N/A')}</div>
            </div>
        `;
        console.log('✅ Sales notification displayed');
    } else {
        const salesDiv = document.getElementById('sales-notification');
        salesDiv.style.display = 'none';
        console.log('⚠️ No sales notification to display');
    }
    
    // If neither response, show message
    if ((!forwarderAcknowledgment || forwarderAcknowledgment.error) && 
        (!salesNotification || salesNotification.error)) {
        const mainResponse = document.getElementById('main-response');
        mainResponse.style.display = 'block';
        mainResponse.innerHTML = `
            <h3>⚠️ No Response Generated</h3>
            <p>No acknowledgment or sales notification was generated from the workflow.</p>
            <p class="message message-warning">Check the workflow state to see what happened.</p>
        `;
        console.log('⚠️ No responses generated');
    }
}

// Handle forwarder form submission
async function handleForwarderSubmit(e) {
    e.preventDefault();
    
    console.log('📧 Forwarder form submitted');
    
    // Immediate visual feedback
    const forwarderBtn = e.target.querySelector('button[type="submit"]') || e.target;
    const originalText = forwarderBtn.innerHTML;
    forwarderBtn.disabled = true;
    forwarderBtn.style.opacity = '0.7';
    forwarderBtn.innerHTML = '⏳ Processing...';
    
    showStatus('✅', 'Forwarder response button clicked!');
    
    const subject = document.getElementById('forwarder-subject').value.trim();
    const content = document.getElementById('forwarder-content').value.trim();
    
    // Get forwarder email from last email's forwarder assignment
    const lastEmail = state.emailHistory[state.emailHistory.length - 1];
    if (!lastEmail || !lastEmail.forwarderAssignment) {
        showStatus('❌', 'Error: No forwarder assignment found');
        forwarderBtn.disabled = false;
        forwarderBtn.style.opacity = '1';
        forwarderBtn.innerHTML = originalText;
        showMessage('❌ No forwarder assignment found', 'error');
        setTimeout(hideStatus, 3000);
        return;
    }
    
    const forwarderEmail = lastEmail.forwarderAssignment.assigned_forwarder?.email || 'forwarder@example.com';
    const forwarderName = lastEmail.forwarderAssignment.assigned_forwarder?.name || 'Forwarder';
    
    if (!content.trim()) {
        showStatus('❌', 'Error: Content cannot be empty');
        forwarderBtn.disabled = false;
        forwarderBtn.style.opacity = '1';
        forwarderBtn.innerHTML = originalText;
        showMessage('❌ Forwarder response content cannot be empty', 'error');
        setTimeout(hideStatus, 3000);
        return;
    }
    
    showStatus('✅', 'Form validated. Preparing request...');
    
    // Log all 4 fields being sent
    console.log('📤 Sending forwarder response with:');
    console.log('   - Forwarder Email:', forwarderEmail);
    console.log('   - Subject:', subject);
    console.log('   - Content:', content.substring(0, 50) + '...');
    console.log('   - Thread ID:', state.threadId);
    
    showLoading(true);
    hideResponse(); // Clear previous responses
    
    try {
        showStatus('🌐', 'Calling API with forwarder email...');
        console.log('🌐 Calling API:', `${state.apiBaseUrl}/api/process-email`);
        
        const startTime = Date.now();
        const response = await fetch(`${state.apiBaseUrl}/api/process-email`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sender: forwarderEmail,      // ✅ Forwarder email
                subject: subject,            // ✅ Subject
                content: content,            // ✅ Content
                thread_id: state.threadId    // ✅ Current thread ID
            })
        });
        
        const responseTime = Date.now() - startTime;
        console.log(`⏱️ API response received in ${responseTime}ms`);
        
        if (!response.ok) {
            showStatus('❌', `API Error: HTTP ${response.status}`);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        showStatus('📥', 'Response received. Extracting data...');
        const data = await response.json();
        
        console.log('✅ API Response received:', { 
            success: data.success, 
            thread_id: data.thread_id 
        });
        
        if (!data.success) {
            showStatus('❌', `Error: ${data.error || 'Unknown error'}`);
            throw new Error(data.error || 'Unknown error occurred');
        }
        
        showStatus('🔍', 'Processing workflow responses...');
        const workflowState = data.result;
        
        // Extract both responses
        const forwarderAcknowledgment = workflowState.acknowledgment_response_result;
        const salesNotification = workflowState.sales_notification_result;
        
        console.log('📋 Extracted responses:');
        console.log('   - Forwarder Acknowledgment:', forwarderAcknowledgment ? 'Present' : 'Missing');
        console.log('   - Sales Notification:', salesNotification ? 'Present' : 'Missing');
        
        showStatus('📤', 'Displaying responses...');
        
        // Create history entry with both responses
        const historyEntry = {
            timestamp: formatAbuDhabiTimestamp(),
            type: 'Forwarder',
            sender: forwarderEmail,
            subject: subject,
            content: content,
            response: forwarderAcknowledgment, // Primary response (acknowledgment)
            responseType: forwarderAcknowledgment ? 'Forwarder Acknowledgment' : 
                         (salesNotification ? 'Sales Notification' : 'No Response'),
            forwarderAssignment: null,
            forwarderResponse: null,
            salesNotification: salesNotification, // Secondary response (sales notification)
            workflowState: workflowState
        };
        
        state.emailHistory.push(historyEntry);
        
        // Display both responses IMMEDIATELY (optimized - show first)
        displayForwarderResponses(forwarderAcknowledgment, salesNotification);
        
        // Display agent performance in sidebar
        displayAgentPerformance(workflowState);
        
        // Hide loading immediately after displaying responses
        showLoading(false);
        showStatus('✅', 'Forwarder response processed successfully!');
        
        // Reset button
        forwarderBtn.disabled = false;
        forwarderBtn.style.opacity = '1';
        forwarderBtn.innerHTML = originalText;
        
        // Show success message immediately
        showMessage('✅ Forwarder response processed!', 'success');
        
        // Hide status after 3 seconds
        setTimeout(() => {
            hideStatus();
        }, 3000);
        
        // Defer heavy operations to avoid blocking UI
        requestAnimationFrame(() => {
            // Save state (non-blocking)
            saveState();
            // Update history display (non-blocking)
            updateHistoryDisplay();
        });
        
        // REMOVED: location.reload() - responses now display immediately
        
    } catch (error) {
        console.error('❌ Error processing forwarder response:', error);
        console.error('Error details:', {
            message: error.message,
            forwarderEmail: forwarderEmail,
            threadId: state.threadId
        });
        
        showStatus('❌', `Error: ${error.message}`);
        showMessage(`❌ Error: ${error.message}`, 'error');
        
        // Reset button on error
        forwarderBtn.disabled = false;
        forwarderBtn.style.opacity = '1';
        forwarderBtn.innerHTML = originalText;
        
        // Hide status after 5 seconds on error
        setTimeout(() => {
            hideStatus();
        }, 5000);
    } finally {
        showLoading(false);
    }
}

// Update history display (optimized - only update if changed)
let lastHistoryCount = 0;

function updateHistoryDisplay() {
    const container = document.getElementById('history-container');
    const count = state.emailHistory.length;
    
    // Quick update of count
    document.getElementById('history-count').textContent = count;
    
    // Only rebuild if history changed (optimization)
    if (count === lastHistoryCount && count > 0) {
        return; // Skip if no new emails
    }
    lastHistoryCount = count;
    
    if (count === 0) {
        container.innerHTML = '<div class="message message-info">ℹ️ No email history yet. Process an email to see it here.</div>';
        return;
    }
    
    // Use DocumentFragment for faster DOM updates
    const fragment = document.createDocumentFragment();
    const tempDiv = document.createElement('div');
    
    // Display in reverse chronological order (newest first)
    const reversed = [...state.emailHistory].reverse();
    
    tempDiv.innerHTML = reversed.map((email, idx) => {
        const emailNum = count - idx;
        const isExpanded = idx === 0;
        
        return `
            <div class="history-item">
                <div class="history-item-header ${isExpanded ? 'expanded' : ''}" onclick="toggleHistoryItem(${count - idx - 1})">
                    <span>📧 Email #${emailNum}: ${email.type} - ${email.subject} (${email.timestamp})</span>
                    <span>${isExpanded ? '▲' : '▼'}</span>
                </div>
                <div class="history-item-content ${isExpanded ? 'expanded' : ''}">
                    <p><strong>⏰ Timestamp:</strong> ${email.timestamp}</p>
                    <p><strong>👤 Type:</strong> ${email.type}</p>
                    <div class="two-columns">
                        <div class="email-content">
                            <h4>📤 Email Sent</h4>
                            <p><strong>From:</strong> <code>${email.sender}</code></p>
                            <p><strong>Subject:</strong> ${email.subject}</p>
                            <p><strong>Content:</strong></p>
                            <pre>${escapeHtml(email.content)}</pre>
                        </div>
                        <div class="response-content">
                            <h4>📥 Response (${email.responseType || 'N/A'})</h4>
                            ${email.response && !email.response.error ? `
                                <p><strong>Subject:</strong> ${email.response.subject || 'N/A'}</p>
                                ${email.response.to ? `<p><strong>To:</strong> <code>${email.response.to}</code></p>` : ''}
                                <p><strong>Body:</strong></p>
                                <pre>${escapeHtml(email.response.body || 'N/A')}</pre>
                            ` : '<p class="message message-info">ℹ️ No response generated or response has error</p>'}
                        </div>
                    </div>
                    ${email.forwarderAssignment ? `
                        <hr style="margin: 20px 0;">
                        <h4>🚚 Forwarder Assignment</h4>
                        <p><strong>Forwarder:</strong> ${email.forwarderAssignment.assigned_forwarder?.name || 'N/A'}</p>
                        <p><strong>Email:</strong> ${email.forwarderAssignment.assigned_forwarder?.email || 'N/A'}</p>
                    ` : ''}
                    ${email.forwarderResponse && !email.forwarderResponse.error ? `
                        <hr style="margin: 20px 0;">
                        <h4>📊 Forwarder Response</h4>
                        <p><strong>Rate:</strong> ${email.forwarderResponse.extracted_rate_info?.rate || 'N/A'}</p>
                        <p><strong>Transit Time:</strong> ${email.forwarderResponse.extracted_rate_info?.transit_time || 'N/A'}</p>
                    ` : ''}
                    ${email.salesNotification && !email.salesNotification.error ? `
                        <hr style="margin: 20px 0;">
                        <h4>📧 Sales Notification</h4>
                        <p><strong>Subject:</strong> ${email.salesNotification.subject || 'N/A'}</p>
                        <details>
                            <summary>View Sales Notification Body</summary>
                            <pre>${escapeHtml(email.salesNotification.body || 'N/A')}</pre>
                        </details>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
    
    // Use innerHTML in one operation (faster than multiple DOM operations)
    container.innerHTML = tempDiv.innerHTML;
}

// Toggle history item
function toggleHistoryItem(index) {
    const items = document.querySelectorAll('.history-item');
    const item = items[state.emailHistory.length - 1 - index];
    if (!item) return;
    
    const header = item.querySelector('.history-item-header');
    const content = item.querySelector('.history-item-content');
    
    const isExpanded = content.classList.contains('expanded');
    
    if (isExpanded) {
        header.classList.remove('expanded');
        content.classList.remove('expanded');
        header.querySelector('span:last-child').textContent = '▼';
    } else {
        header.classList.add('expanded');
        content.classList.add('expanded');
        header.querySelector('span:last-child').textContent = '▲';
    }
}

// Forwarder form removed - forwarder emails are now sent through main form
// This function is kept for backward compatibility but does nothing
// Form auto-population happens in displayResponse() when forwarder is assigned
function checkForwarderForm() {
    // No longer needed - forwarder emails use main form
    return;
}

// Reset thread
function resetThread() {
    if (confirm('Are you sure you want to reset the thread? This will clear all email history.')) {
        generateThreadId();
        state.emailHistory = [];
        saveState();
        updateUI();
        hideResponse();
        showMessage('✅ Thread reset! Email history cleared.', 'success');
    }
}

// Toggle sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('agent-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    if (sidebar && overlay) {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('active');
    }
}

// Get agent status
function getAgentStatus(agentResult) {
    if (!agentResult) {
        return { status: 'not-executed', icon: '⏳', color: '#9E9E9E', label: 'Not Executed' };
    }
    if (agentResult.error) {
        return { status: 'error', icon: '❌', color: '#f44336', label: 'Error' };
    }
    if (agentResult.warning) {
        return { status: 'warning', icon: '⚠️', color: '#FF9800', label: 'Warning' };
    }
    return { status: 'success', icon: '✅', color: '#4CAF50', label: 'Success' };
}

// Extract agent summary
function extractAgentSummary(agentKey, agentResult) {
    if (!agentResult || agentResult.error) {
        return agentResult?.error || 'No result';
    }
    
    // Extract key information based on agent type
    switch (agentKey) {
        case 'classification_result':
            return `Email Type: ${agentResult.email_type || 'N/A'}`;
        case 'conversation_state_result':
            return `State: ${agentResult.conversation_state || 'N/A'}`;
        case 'extraction_result':
            const extracted = agentResult.extracted_data || {};
            const count = Object.keys(extracted).length;
            return `Extracted ${count} categories`;
        case 'validation_result':
            const missing = agentResult.missing_fields || [];
            return missing.length > 0 ? `${missing.length} missing fields` : 'All fields valid';
        case 'port_lookup_result':
            return `Ports: ${agentResult.origin_port?.port_code || 'N/A'} → ${agentResult.destination_port?.port_code || 'N/A'}`;
        case 'next_action_result':
            return `Action: ${agentResult.next_action || 'N/A'}`;
        case 'forwarder_assignment_result':
            return `Forwarder: ${agentResult.assigned_forwarder?.name || 'N/A'}`;
        case 'sales_notification_result':
            return `Notification Type: ${agentResult.notification_type || 'N/A'}`;
        default:
            return 'Completed successfully';
    }
}

// Display agent performance
function displayAgentPerformance(workflowState) {
    const agents = [
        { key: 'classification_result', name: 'Email Classifier', icon: '📧', category: 'core' },
        { key: 'conversation_state_result', name: 'Conversation State', icon: '💬', category: 'core' },
        { key: 'thread_analysis_result', name: 'Thread Analysis', icon: '🔍', category: 'core' },
        { key: 'extraction_result', name: 'Information Extraction', icon: '📝', category: 'core' },
        { key: 'validation_result', name: 'Data Validation', icon: '✅', category: 'core' },
        { key: 'port_lookup_result', name: 'Port Lookup', icon: '🌍', category: 'core' },
        { key: 'container_standardization_result', name: 'Container Standardization', icon: '📦', category: 'core' },
        { key: 'rate_recommendation_result', name: 'Rate Recommendation', icon: '💰', category: 'core' },
        { key: 'next_action_result', name: 'Next Action', icon: '🎯', category: 'core' },
        { key: 'clarification_response_result', name: 'Clarification Response', icon: '❓', category: 'response' },
        { key: 'confirmation_response_result', name: 'Confirmation Response', icon: '✓', category: 'response' },
        { key: 'acknowledgment_response_result', name: 'Acknowledgment', icon: '👋', category: 'response' },
        { key: 'confirmation_acknowledgment_result', name: 'Confirmation Acknowledgment', icon: '✅', category: 'response' },
        { key: 'customer_quote_result', name: 'Customer Quote', icon: '📨', category: 'response' },
        { key: 'forwarder_detection_result', name: 'Forwarder Detection', icon: '🚚', category: 'forwarder' },
        { key: 'forwarder_response_result', name: 'Forwarder Response', icon: '📧', category: 'forwarder' },
        { key: 'forwarder_email_draft_result', name: 'Forwarder Email Draft', icon: '✍️', category: 'forwarder' },
        { key: 'forwarder_assignment_result', name: 'Forwarder Assignment', icon: '📋', category: 'forwarder' },
        { key: 'escalation_result', name: 'Escalation', icon: '⚠️', category: 'other' },
        { key: 'sales_notification_result', name: 'Sales Notification', icon: '📧', category: 'other' },
    ];
    
    const timeline = document.getElementById('agent-timeline');
    if (!timeline) return;
    
    // Count executed agents
    let executedCount = 0;
    let successCount = 0;
    let errorCount = 0;
    let warningCount = 0;
    
    // Generate agent cards
    const agentCards = agents.map((agent, index) => {
        const agentResult = workflowState[agent.key];
        const status = getAgentStatus(agentResult);
        
        if (agentResult) {
            executedCount++;
            if (status.status === 'success') successCount++;
            else if (status.status === 'error') errorCount++;
            else if (status.status === 'warning') warningCount++;
        }
        
        const summary = extractAgentSummary(agent.key, agentResult);
        const confidence = agentResult?.confidence || agentResult?.confidence_score || null;
        
        return `
            <div class="agent-card ${status.status}" data-agent="${agent.key}" onclick="toggleAgentDetails('${agent.key}')">
                <div class="agent-card-header">
                    <div class="agent-name">
                        <span>${agent.icon}</span>
                        <span>${agent.name}</span>
                    </div>
                    <span class="agent-status-badge">${status.icon}</span>
                </div>
                <div class="agent-summary-text">${summary}</div>
                ${confidence ? `<div class="agent-confidence">Confidence: ${(confidence * 100).toFixed(0)}%</div>` : ''}
                <div class="agent-details-toggle" onclick="event.stopPropagation(); toggleAgentDetails('${agent.key}')">
                    <span id="toggle-${agent.key}">▼</span> View Details
                </div>
                <div class="agent-details" id="details-${agent.key}">
                    <pre>${JSON.stringify(agentResult || { status: 'not_executed' }, null, 2)}</pre>
                </div>
            </div>
        `;
    }).join('');
    
    timeline.innerHTML = agentCards;
    
    // Update execution status
    const statusBadge = document.getElementById('status-badge');
    const agentCount = document.getElementById('agent-count');
    
    if (statusBadge && agentCount) {
        if (errorCount > 0) {
            statusBadge.textContent = `❌ ${errorCount} Error(s)`;
            statusBadge.style.color = '#f44336';
        } else if (warningCount > 0) {
            statusBadge.textContent = `⚠️ ${warningCount} Warning(s)`;
            statusBadge.style.color = '#FF9800';
        } else if (executedCount > 0) {
            statusBadge.textContent = '✅ Complete';
            statusBadge.style.color = '#4CAF50';
        } else {
            statusBadge.textContent = '⏳ Waiting...';
            statusBadge.style.color = '#666';
        }
        
        agentCount.textContent = `${executedCount}/20 Agents Executed`;
    }
    
    // Update summary
    const summaryDiv = document.getElementById('agent-summary');
    const summaryStats = document.getElementById('summary-stats');
    
    if (summaryDiv && summaryStats && executedCount > 0) {
        summaryDiv.style.display = 'block';
        const successRate = executedCount > 0 ? ((successCount / executedCount) * 100).toFixed(0) : 0;
        
        summaryStats.innerHTML = `
            <div class="summary-stat">
                <span class="summary-stat-label">Success Rate:</span>
                <span class="summary-stat-value">${successRate}%</span>
            </div>
            <div class="summary-stat">
                <span class="summary-stat-label">Successful:</span>
                <span class="summary-stat-value" style="color: #4CAF50;">${successCount}</span>
            </div>
            <div class="summary-stat">
                <span class="summary-stat-label">Errors:</span>
                <span class="summary-stat-value" style="color: #f44336;">${errorCount}</span>
            </div>
            <div class="summary-stat">
                <span class="summary-stat-label">Warnings:</span>
                <span class="summary-stat-value" style="color: #FF9800;">${warningCount}</span>
            </div>
        `;
    }
}

// Toggle agent details
function toggleAgentDetails(agentKey) {
    const details = document.getElementById(`details-${agentKey}`);
    const toggle = document.getElementById(`toggle-${agentKey}`);
    
    if (details && toggle) {
        const isExpanded = details.classList.contains('expanded');
        if (isExpanded) {
            details.classList.remove('expanded');
            toggle.textContent = '▼';
        } else {
            details.classList.add('expanded');
            toggle.textContent = '▲';
        }
    }
}

// Utility functions
function showLoading(show) {
    document.getElementById('loading-spinner').style.display = show ? 'block' : 'none';
    document.getElementById('process-btn').disabled = show;
}

function hideResponse() {
    document.getElementById('response-section').style.display = 'none';
    // Clear all response sections including forwarder acknowledgment and sales notification
    ['main-response', 'forwarder-assignment', 'forwarder-response', 
     'forwarder-acknowledgment', 'sales-notification', 'customer-quote', 'debug-section'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.style.display = 'none';
            el.innerHTML = '';
        }
    });
}

function showMessage(message, type) {
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.textContent = message;
    
    // Insert at top of container
    const container = document.querySelector('.container');
    container.insertBefore(messageDiv, container.firstChild);
    
    // Remove after 5 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);

