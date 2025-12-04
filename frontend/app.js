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

// Save state to localStorage
function saveState() {
    localStorage.setItem('threadId', state.threadId);
    localStorage.setItem('emailHistory', JSON.stringify(state.emailHistory));
}

// Generate new thread ID
function generateThreadId() {
    const now = new Date();
    const timestamp = now.toISOString()
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
    
    // Forwarder form submission
    const forwarderForm = document.getElementById('forwarder-form');
    if (forwarderForm) {
        forwarderForm.addEventListener('submit', handleForwarderSubmit);
        console.log('✅ Forwarder form listener added');
    } else {
        console.log('ℹ️ Forwarder form not found (this is OK if not shown yet)');
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
    
    // Check for forwarder form
    checkForwarderForm();
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
    
    const sender = document.getElementById('sender-email').value.trim();
    const subject = document.getElementById('subject').value.trim();
    const content = document.getElementById('content').value.trim();
    const emailType = document.getElementById('email-type').value;
    
    console.log('📝 Form data:', { sender, subject, content: content.substring(0, 50) + '...', emailType });
    
    if (!content) {
        showMessage('❌ Email content cannot be empty', 'error');
        return;
    }
    
    // Show loading
    showLoading(true);
    hideResponse();
    
    console.log('🌐 Calling API:', `${state.apiBaseUrl}/api/process-email`);
    
    try {
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
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Unknown error occurred');
        }
        
        // Update thread ID if changed
        if (data.thread_id && data.thread_id !== state.threadId) {
            state.threadId = data.thread_id;
            saveState();
        }
        
        // Process response
        processWorkflowResponse(data, emailType, sender, subject, content);
        
        // Update form state
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
        showMessage(`❌ Error processing email: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Process workflow response
function processWorkflowResponse(data, emailType, sender, subject, content) {
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
        timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
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
    saveState();
    
    // Display response
    displayResponse(response, responseType, forwarderAssignment, forwarderResponse, 
                    salesNotification, customerQuote, workflowState, emailType);
    
    // Update history display
    updateHistoryDisplay();
    
    // Check for forwarder form
    checkForwarderForm();
    
    // Show success
    showMessage('✅ Email processed successfully!', 'success');
}

// Display response
function displayResponse(response, responseType, forwarderAssignment, forwarderResponse,
                        salesNotification, customerQuote, workflowState, emailType) {
    const responseSection = document.getElementById('response-section');
    responseSection.style.display = 'block';
    
    // Main response
    const mainResponse = document.getElementById('main-response');
    if (response && !response.error) {
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
                    <p><strong>Route:</strong> ${forwarderAssignment.origin_country || 'N/A'} → ${forwarderAssignment.destination_country || 'N/A'}</p>
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
    
    // Forwarder Acknowledgment
    if (workflowState.acknowledgment_response_result) {
        const ack = workflowState.acknowledgment_response_result;
        if ((ack.sender_type === 'forwarder' || emailType === 'Forwarder') && !ack.error) {
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

// Handle forwarder form submission
async function handleForwarderSubmit(e) {
    e.preventDefault();
    
    const subject = document.getElementById('forwarder-subject').value.trim();
    const content = document.getElementById('forwarder-content').value.trim();
    
    // Get forwarder email from last email's forwarder assignment
    const lastEmail = state.emailHistory[state.emailHistory.length - 1];
    if (!lastEmail || !lastEmail.forwarderAssignment) {
        showMessage('❌ No forwarder assignment found', 'error');
        return;
    }
    
    const forwarderEmail = lastEmail.forwarderAssignment.assigned_forwarder?.email || 'forwarder@example.com';
    
    showLoading(true);
    
    try {
        const response = await fetch(`${state.apiBaseUrl}/api/process-email`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sender: forwarderEmail,
                subject: subject,
                content: content,
                thread_id: state.threadId
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Unknown error occurred');
        }
        
        const workflowState = data.result;
        
        // Find response
        let responseObj = null;
        let responseType = null;
        
        if (workflowState.sales_notification_result) {
            responseObj = workflowState.sales_notification_result;
            responseType = 'Sales Notification';
        } else if (workflowState.acknowledgment_response_result) {
            responseObj = workflowState.acknowledgment_response_result;
            responseType = 'Forwarder Acknowledgment';
        }
        
        // Add to history
        const historyEntry = {
            timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
            type: 'Forwarder',
            sender: forwarderEmail,
            subject: subject,
            content: content,
            response: responseObj,
            responseType: responseType,
            forwarderAssignment: null,
            forwarderResponse: null,
            salesNotification: workflowState.sales_notification_result,
            workflowState: workflowState
        };
        
        state.emailHistory.push(historyEntry);
        saveState();
        
        updateHistoryDisplay();
        checkForwarderForm();
        showMessage('✅ Forwarder response processed!', 'success');
        
        // Reload page to show new response
        location.reload();
        
    } catch (error) {
        console.error('Error processing forwarder response:', error);
        showMessage(`❌ Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Update history display
function updateHistoryDisplay() {
    const container = document.getElementById('history-container');
    const count = state.emailHistory.length;
    
    document.getElementById('history-count').textContent = count;
    
    if (count === 0) {
        container.innerHTML = '<div class="message message-info">ℹ️ No email history yet. Process an email to see it here.</div>';
        return;
    }
    
    // Display in reverse chronological order (newest first)
    const reversed = [...state.emailHistory].reverse();
    
    container.innerHTML = reversed.map((email, idx) => {
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

// Check if forwarder form should be shown
function checkForwarderForm() {
    const forwarderSection = document.getElementById('forwarder-form-section');
    if (!forwarderSection) return;
    
    const lastEmail = state.emailHistory[state.emailHistory.length - 1];
    if (lastEmail && lastEmail.forwarderAssignment) {
        forwarderSection.style.display = 'block';
        
        // Pre-fill forwarder form
        const assignedForwarder = lastEmail.forwarderAssignment.assigned_forwarder || {};
        const forwarderName = assignedForwarder.name || 'Forwarder Team';
        
        document.getElementById('forwarder-content').value = `Dear Logistics Team,

Please find our rate quote:

Route: Shanghai (CNSHG) to Los Angeles (USLAX)
Container: 40HC
Rate: $2,850 USD
Transit Time: 18 days
Valid Until: December 31, 2024

Please confirm if you would like to proceed.

Best regards,
${forwarderName}`;
    } else {
        forwarderSection.style.display = 'none';
    }
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

// Utility functions
function showLoading(show) {
    document.getElementById('loading-spinner').style.display = show ? 'block' : 'none';
    document.getElementById('process-btn').disabled = show;
}

function hideResponse() {
    document.getElementById('response-section').style.display = 'none';
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

