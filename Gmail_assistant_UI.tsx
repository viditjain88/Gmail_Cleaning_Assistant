import { useState } from 'react';

export default function GmailCleaningAssistant() {
  const [emails, setEmails] = useState([
    {
      id: 'e001',
      subject: 'Your Amazon Order #123-4567890-1234567',
      reason: 'DELETE | Promotional email from Amazon with order confirmation that is 3 months old',
      size: 12.3,
      selected: true
    },
    {
      id: 'e002',
      subject: 'Weekly Newsletter: 10 Tech Stories You Should Read',
      reason: 'DELETE | Newsletter with outdated content from last month',
      size: 45.8,
      selected: true
    },
    {
      id: 'e003', 
      subject: '[SALE] 50% Off Everything This Weekend Only!',
      reason: 'DELETE | Promotional sale email that has expired',
      size: 28.2,
      selected: false
    },
    {
      id: 'e004',
      subject: 'Your subscription will renew automatically',
      reason: 'DELETE | Notification about service you already cancelled',
      size: 9.6,
      selected: true
    },
  ]);
  
  const [selectAll, setSelectAll] = useState(false);
  
  const toggleSelectAll = () => {
    const newSelectAll = !selectAll;
    setSelectAll(newSelectAll);
    setEmails(emails.map(email => ({...email, selected: newSelectAll})));
  };
  
  const toggleEmailSelected = (id) => {
    setEmails(emails.map(email => 
      email.id === id ? {...email, selected: !email.selected} : email
    ));
  };
  
  const selectedCount = emails.filter(e => e.selected).length;
  const totalSize = emails.filter(e => e.selected).reduce((sum, e) => sum + e.size, 0);
  
  return (
    <div className="flex flex-col p-8 max-w-4xl mx-auto bg-white shadow-lg rounded-lg">
      <h1 className="text-2xl font-bold mb-6">Gmail Storage Cleanup Assistant</h1>
      
      <div className="bg-blue-50 p-4 rounded-lg mb-6">
        <h2 className="text-lg font-semibold mb-2">Storage Cleanup Recommendations</h2>
        <p className="text-blue-800">Total space that can be saved: 0.09 MB</p>
      </div>
      
      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-4">Select emails to delete:</h2>
        
        <div className="flex items-center mb-2">
          <input 
            type="checkbox" 
            className="mr-2 h-4 w-4"
            checked={selectAll}
            onChange={toggleSelectAll}
          />
          <span className="font-medium">Select/Deselect All</span>
        </div>
        
        <div className="border rounded-lg overflow-hidden">
          {/* Table Header */}
          <div className="grid grid-cols-12 bg-gray-100 p-3 text-sm font-medium">
            <div className="col-span-1">Select</div>
            <div className="col-span-5">Subject</div>
            <div className="col-span-5">Reason for Deletion</div>
            <div className="col-span-1 text-right">Size</div>
          </div>
          
          {/* Table Rows */}
          {emails.map(email => (
            <div key={email.id} className="grid grid-cols-12 border-t p-3 text-sm hover:bg-gray-50">
              <div className="col-span-1">
                <input 
                  type="checkbox" 
                  className="h-4 w-4"
                  checked={email.selected}
                  onChange={() => toggleEmailSelected(email.id)}
                />
              </div>
              <div className="col-span-5 truncate font-medium">{email.subject}</div>
              <div className="col-span-5 truncate text-gray-600">
                {email.reason.includes('|') ? email.reason.split('|')[1].trim() : email.reason}
              </div>
              <div className="col-span-1 text-right">{email.size.toFixed(1)} KB</div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
        <div className="text-sm">
          <span className="font-medium">{selectedCount} emails selected</span>
          <span className="mx-2">·</span>
          <span>{totalSize.toFixed(2)} KB total</span>
        </div>
        
        <button 
          className="bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg font-medium"
        >
          Delete Selected Emails
        </button>
      </div>
      
      <div className="mt-6 text-xs text-gray-500">
        Email content is processed locally. No data is stored permanently.
      </div>
    </div>
  );
}
