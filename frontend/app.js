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
        : 'http://localhost:5001'  // Change this if the API runs on a different host/port
};

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

function init() {
    loadState();
    setupEventListeners();
    updateUI();
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

// Save state to localStorage, deferred so it never blocks the UI thread
function saveState() {
    try {
        setTimeout(() => {
            localStorage.setItem('threadId', state.threadId);
            localStorage.setItem('emailHistory', JSON.stringify(state.emailHistory));
        }, 0);
    } catch (e) {
        console.warn('Failed to save state to localStorage:', e);
    }
}

// Current time in Abu Dhabi timezone (UTC+4)
function getAbuDhabiTime() {
    const now = new Date();
    const abuDhabiOffset = 4 * 60; // minutes
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

function setupEventListeners() {
    const resetBtn = document.getElementById('reset-thread-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetThread);
    } else {
        console.error('Reset thread button not found');
    }

    const templateSelector = document.getElementById('template-selector');
    if (templateSelector) {
        templateSelector.addEventListener('change', handleTemplateSelect);
    } else {
        console.error('Template selector not found');
    }

    const emailType = document.getElementById('email-type');
    if (emailType) {
        emailType.addEventListener('change', handleEmailTypeChange);
    } else {
        console.error('Email type selector not found');
    }

    const emailForm = document.getElementById('email-form');
    if (emailForm) {
        emailForm.addEventListener('submit', handleEmailSubmit);
    } else {
        console.error('Email form not found');
    }

    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }

    const sidebarClose = document.getElementById('sidebar-close');
    if (sidebarClose) {
        sidebarClose.addEventListener('click', toggleSidebar);
    }

    const sidebarOverlay = document.getElementById('sidebar-overlay');
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', toggleSidebar);
    }
}

// Render current state into the form and history
function updateUI() {
    document.getElementById('thread-id').textContent = state.threadId;

    document.getElementById('email-type').value = state.formState.emailType;
    document.getElementById('sender-email').value = state.formState.senderEmail;
    document.getElementById('subject').value = state.formState.subject;
    document.getElementById('content').value = state.formState.content;

    updateSenderEmailLabel();
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

// Show the on-screen status indicator and mirror it to the console
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

    state.formState.emailType = template.type;
    state.formState.senderEmail = template.sender;
    state.formState.subject = template.subject;
    state.formState.content = template.content;
    state.selectedTemplate = templateKey;

    updateUI();

    const messageDiv = document.getElementById('template-message');
    messageDiv.textContent = `✅ Loaded template: ${e.target.options[e.target.selectedIndex].text}`;
    messageDiv.style.display = 'block';
    
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 3000);
}

async function handleEmailSubmit(e) {
    e.preventDefault();

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

    if (!content) {
        showStatus('❌', 'Error: Email content cannot be empty');
        if (processBtn) processBtn.disabled = false;
        if (processBtnText) processBtnText.style.display = 'inline';
        if (processBtnSpinner) processBtnSpinner.style.display = 'none';
        showMessage('❌ Email content cannot be empty', 'error');
        setTimeout(hideStatus, 3000);
        return;
    }
    
    showLoading(true);
    showStatus('⏳', 'Form validated. Calling API...');
    hideResponse();

    // Scroll to top so the loading spinner is visible
    window.scrollTo({ top: 0, behavior: 'smooth' });

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
        console.log(`API response received in ${responseTime}ms`);

        if (!response.ok) {
            showStatus('❌', `API Error: HTTP ${response.status}`);
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        showStatus('📥', 'Response received. Processing...');
        const data = await response.json();

        if (!data.success) {
            showStatus('❌', `Error: ${data.error || 'Unknown error'}`);
            throw new Error(data.error || 'Unknown error occurred');
        }
        
        showStatus('✅', 'Processing workflow response...');

        if (data.thread_id && data.thread_id !== state.threadId) {
            state.threadId = data.thread_id;
            saveState();
        }

        processWorkflowResponse(data, emailType, sender, subject, content, processBtn, processBtnText, processBtnSpinner);

        state.formState.senderEmail = sender;
        state.formState.subject = subject;
        state.formState.content = content;

    } catch (error) {
        console.error('Error processing email:', error);

        showStatus('❌', `Error: ${error.message}`);
        showMessage(`❌ Error processing email: ${error.message}`, 'error');

        if (processBtn) {
            processBtn.disabled = false;
            processBtn.style.opacity = '1';
        }
        if (processBtnText) processBtnText.style.display = 'inline';
        if (processBtnSpinner) processBtnSpinner.style.display = 'none';

        setTimeout(hideStatus, 5000);
    } finally {
        showLoading(false);
    }
}

function processWorkflowResponse(data, emailType, sender, subject, content, processBtn = null, processBtnText = null, processBtnSpinner = null) {
    const workflowState = data.result;

    // Pick the response to surface, in priority order
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
    
    const forwarderAssignment = workflowState.forwarder_assignment_result;
    const forwarderResponse = workflowState.forwarder_response_result;
    const salesNotification = workflowState.sales_notification_result;
    const customerQuote = workflowState.customer_quote_result;

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
    
    state.emailHistory.push(historyEntry);

    showStatus('📤', 'Displaying response...');
    displayResponse(response, responseType, forwarderAssignment, forwarderResponse,
                    salesNotification, customerQuote, workflowState, emailType);

    displayAgentPerformance(workflowState);

    showLoading(false);
    showStatus('✅', 'Response displayed successfully!');

    if (processBtn) {
        processBtn.disabled = false;
        processBtn.style.opacity = '1';
    }
    if (processBtnText) processBtnText.style.display = 'inline';
    if (processBtnSpinner) processBtnSpinner.style.display = 'none';

    showMessage('✅ Email processed successfully!', 'success');

    setTimeout(hideStatus, 3000);

    // Defer the heavier persistence/history work so it doesn't block the render
    requestAnimationFrame(() => {
        saveState();
        updateHistoryDisplay();
    });
}

function displayResponse(response, responseType, forwarderAssignment, forwarderResponse,
                        salesNotification, customerQuote, workflowState, emailType) {
    const responseSection = document.getElementById('response-section');
    responseSection.style.display = 'block';
    responseSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

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
                    <p><strong>Route:</strong> ${forwarderAssignment.origin_country || 'Unknown'} → ${forwarderAssignment.destination_country || 'Unknown'}</p>
                    <p><strong>Why this forwarder:</strong> ${escapeHtml(forwarderAssignment.assignment_reason || 'Assigned from available forwarders.')}</p>
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
        
        // Pre-populate the main form so the user can reply as the forwarder
        const forwarderEmail = assignedForwarder.email;
        const forwarderName = assignedForwarder.name || 'Forwarder Team';
        const forwarderCompany = assignedForwarder.company || '';

        if (forwarderEmail) {
            const emailTypeSelect = document.getElementById('email-type');
            if (emailTypeSelect) {
                emailTypeSelect.value = 'Forwarder';
                state.formState.emailType = 'Forwarder';
            }

            const senderEmailInput = document.getElementById('sender-email');
            if (senderEmailInput) {
                senderEmailInput.value = forwarderEmail;
                state.formState.senderEmail = forwarderEmail;
            }

            updateSenderEmailLabel();

            const subjectInput = document.getElementById('subject');
            if (subjectInput && !subjectInput.value.trim()) {
                const origin = forwarderAssignment.origin_country || '';
                const dest = forwarderAssignment.destination_country || '';
                const defaultSubject = origin && dest 
                    ? `Rate Quote - ${origin} to ${dest}`
                    : 'Rate Quote - Shipping Request';
                subjectInput.value = defaultSubject;
            }
            
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

            showMessage('✅ Forwarder assigned! You can now send email as forwarder using the form above.', 'info');

            // Scroll to the form once the fields above have been updated
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
    
    // Forwarder rate is now surfaced in the collated Sales Notification below,
    // so the standalone rates card stays hidden.
    const forwarderRespDiv = document.getElementById('forwarder-response');
    if (forwarderRespDiv) forwarderRespDiv.style.display = 'none';

    // Sales Notification
    if (salesNotification && !salesNotification.error) {
        const salesDiv = document.getElementById('sales-notification');
        salesDiv.style.display = 'block';
        salesDiv.innerHTML = `
            <h3>📧 Collated Email → Sales Team</h3>
            <p class="message message-info">Internal hand-off: customer requirements + forwarder cost rate. Sales adds their markup, then contacts the customer. <strong>Not sent to the customer.</strong></p>
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
    
    // Forwarder emails are handled by displayForwarderResponses(); only show the
    // acknowledgment here for non-forwarder emails to avoid duplication.
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
    
    // Show the raw workflow state when there is no usable response
    if (!response || response.error) {
        const debugDiv = document.getElementById('debug-section');
        debugDiv.style.display = 'block';
        debugDiv.innerHTML = `
            <h3>🔍 Debug: Workflow State</h3>
            <pre>${JSON.stringify(workflowState, null, 2)}</pre>
        `;
    }
}

// Render the forwarder reply: acknowledgment, sales notification and customer quote
function displayForwarderResponses(forwarderAcknowledgment, salesNotification, customerQuote) {
    const responseSection = document.getElementById('response-section');
    responseSection.style.display = 'block';
    responseSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Main response card is not used for forwarder replies
    const mainResponse = document.getElementById('main-response');
    mainResponse.style.display = 'none';
    mainResponse.innerHTML = '';

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
    } else {
        const ackDiv = document.getElementById('forwarder-acknowledgment');
        ackDiv.style.display = 'none';
    }

    if (salesNotification && !salesNotification.error) {
        const salesDiv = document.getElementById('sales-notification');
        salesDiv.style.display = 'block';
        salesDiv.innerHTML = `
            <h3>📧 Collated Email → Sales Team</h3>
            <p class="message message-info">Internal hand-off: customer requirements + forwarder cost rate. Sales adds their markup, then contacts the customer. <strong>Not sent to the customer.</strong></p>
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
    } else {
        const salesDiv = document.getElementById('sales-notification');
        salesDiv.style.display = 'none';
    }

    // Collated final email to the customer, if one was formed
    const quoteDiv = document.getElementById('customer-quote');
    if (customerQuote && !customerQuote.error) {
        quoteDiv.style.display = 'block';
        quoteDiv.innerHTML = `
            <h3>📨 Final Customer Quote Email (Collated)</h3>
            <p class="message message-success">Collated email to the customer with the forwarder's rate.</p>
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
    } else {
        quoteDiv.style.display = 'none';
    }

    // Fall back to a notice when nothing was generated
    if ((!forwarderAcknowledgment || forwarderAcknowledgment.error) &&
        (!salesNotification || salesNotification.error)) {
        const mainResponse = document.getElementById('main-response');
        mainResponse.style.display = 'block';
        mainResponse.innerHTML = `
            <h3>⚠️ No Response Generated</h3>
            <p>No acknowledgment or sales notification was generated from the workflow.</p>
            <p class="message message-warning">Check the workflow state to see what happened.</p>
        `;
    }
}

async function handleForwarderSubmit(e) {
    e.preventDefault();

    const forwarderBtn = e.target.querySelector('button[type="submit"]') || e.target;
    const originalText = forwarderBtn.innerHTML;
    forwarderBtn.disabled = true;
    forwarderBtn.style.opacity = '0.7';
    forwarderBtn.innerHTML = '⏳ Processing...';
    
    showStatus('✅', 'Forwarder response button clicked!');
    
    const subject = document.getElementById('forwarder-subject').value.trim();
    const content = document.getElementById('forwarder-content').value.trim();

    // Forwarder email comes from the most recent forwarder assignment
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

    showLoading(true);
    hideResponse();

    try {
        showStatus('🌐', 'Calling API with forwarder email...');

        const startTime = Date.now();
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

        const responseTime = Date.now() - startTime;
        console.log(`API response received in ${responseTime}ms`);

        if (!response.ok) {
            showStatus('❌', `API Error: HTTP ${response.status}`);
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        showStatus('📥', 'Response received. Extracting data...');
        const data = await response.json();

        if (!data.success) {
            showStatus('❌', `Error: ${data.error || 'Unknown error'}`);
            throw new Error(data.error || 'Unknown error occurred');
        }
        
        showStatus('🔍', 'Processing workflow responses...');
        const workflowState = data.result;

        const forwarderAcknowledgment = workflowState.acknowledgment_response_result;
        const salesNotification = workflowState.sales_notification_result;
        const customerQuote = workflowState.customer_quote_result;

        showStatus('📤', 'Displaying responses...');

        const historyEntry = {
            timestamp: formatAbuDhabiTimestamp(),
            type: 'Forwarder',
            sender: forwarderEmail,
            subject: subject,
            content: content,
            response: forwarderAcknowledgment,
            responseType: forwarderAcknowledgment ? 'Forwarder Acknowledgment' :
                         (salesNotification ? 'Sales Notification' : 'No Response'),
            forwarderAssignment: null,
            forwarderResponse: null,
            salesNotification: salesNotification,
            customerQuote: customerQuote,
            workflowState: workflowState
        };

        state.emailHistory.push(historyEntry);

        displayForwarderResponses(forwarderAcknowledgment, salesNotification, customerQuote);

        displayAgentPerformance(workflowState);

        showLoading(false);
        showStatus('✅', 'Forwarder response processed successfully!');

        forwarderBtn.disabled = false;
        forwarderBtn.style.opacity = '1';
        forwarderBtn.innerHTML = originalText;

        showMessage('✅ Forwarder response processed!', 'success');

        setTimeout(hideStatus, 3000);

        requestAnimationFrame(() => {
            saveState();
            updateHistoryDisplay();
        });

    } catch (error) {
        console.error('Error processing forwarder response:', error);

        showStatus('❌', `Error: ${error.message}`);
        showMessage(`❌ Error: ${error.message}`, 'error');

        forwarderBtn.disabled = false;
        forwarderBtn.style.opacity = '1';
        forwarderBtn.innerHTML = originalText;

        setTimeout(hideStatus, 5000);
    } finally {
        showLoading(false);
    }
}

let lastHistoryCount = 0;

// Rebuild the history list, skipping work when nothing has changed
function updateHistoryDisplay() {
    const container = document.getElementById('history-container');
    const count = state.emailHistory.length;

    document.getElementById('history-count').textContent = count;

    if (count === lastHistoryCount && count > 0) {
        return;
    }
    lastHistoryCount = count;

    if (count === 0) {
        container.innerHTML = '<div class="message message-info">ℹ️ No email history yet. Process an email to see it here.</div>';
        return;
    }

    const tempDiv = document.createElement('div');

    // Newest first
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

// Retained for backward compatibility. Forwarder emails now use the main form,
// which is auto-populated by displayResponse() when a forwarder is assigned.
function checkForwarderForm() {
    return;
}

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

function toggleSidebar() {
    const sidebar = document.getElementById('agent-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    if (sidebar && overlay) {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('active');
    }
}

// Map an agent result to a display status (icon/color/label drive the UI badge)
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

// Build a one-line summary of an agent result for the sidebar card
function extractAgentSummary(agentKey, agentResult) {
    if (!agentResult || agentResult.error) {
        return agentResult?.error || 'No result';
    }

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

// Render the agent performance sidebar from the workflow state
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

    let executedCount = 0;
    let successCount = 0;
    let errorCount = 0;
    let warningCount = 0;

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
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.textContent = message;

    const container = document.querySelector('.container');
    container.insertBefore(messageDiv, container.firstChild);

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

