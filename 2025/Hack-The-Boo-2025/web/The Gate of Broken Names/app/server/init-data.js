import crypto from 'crypto';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Generate random password using crypto
function generateRandomPassword(length = 16) {
  return crypto.randomBytes(length).toString('hex').substring(0, length);
}

// Read flag file
function readFlag() {
  try {
    if (fs.existsSync("/flag.txt")) {
      return fs.readFileSync("/flag.txt", 'utf8').trim();
    }
    return 'HTB{FAKE_FLAG_FOR_TESTING}';
  } catch (error) {
    console.error('Error reading flag:', error);
    return 'HTB{FAKE_FLAG_FOR_TESTING}';
  }
}

// Initialize users with random passwords
export function initializeUsers() {
  const adminPassword = generateRandomPassword(12);
  const miraPassword = generateRandomPassword(12);
  const guestPassword = generateRandomPassword(12);
  const keeperPassword = generateRandomPassword(12);

  console.log('\n🔐 Generated Credentials:');
  console.log('━'.repeat(50));
  console.log(`Admin:  username: admin   | password: ${adminPassword}`);
  console.log(`Mira:   username: mira    | password: ${miraPassword}`);
  console.log(`Guest:  username: guest   | password: ${guestPassword}`);
  console.log(`Keeper: username: keeper  | password: ${keeperPassword}`);
  console.log('━'.repeat(50) + '\n');
  
  return [
    {
      id: 1,
      username: 'admin',
      password: adminPassword,
      role: 'administrator',
      email: 'gatekeeper@caerwyrrd.realm',
      created_at: new Date().toISOString()
    },
    {
      id: 2,
      username: 'mira',
      password: miraPassword,
      role: 'gatewalker',
      email: 'mira@briarfold.realm',
      created_at: new Date().toISOString()
    },
    {
      id: 3,
      username: 'keeper',
      password: keeperPassword,
      role: 'guardian',
      email: 'keeper@seals.realm',
      created_at: new Date().toISOString()
    }
  ];
}

export function initializeSystemNotes() {
  const now = Date.now();
  const dayMs = 24 * 60 * 60 * 1000;
  
  return [
    {
      id: 1,
      user_id: 1,
      title: 'Daily Gate Inspection Report',
      content: 'Completed routine inspection of all registered gates. The Threshold of Names remains partially unsealed. Recommend increased monitoring.',
      is_private: 0,
      created_at: new Date(now - 5 * dayMs).toISOString(),
      updated_at: new Date(now - 5 * dayMs).toISOString()
    },
    {
      id: 2,
      user_id: 1,
      title: 'Security Configuration Notes',
      content: 'Updated firewall rules and access controls. All credentials are randomly generated on startup. Check console logs for current credentials.',
      is_private: 1,
      created_at: new Date(now - 3 * dayMs).toISOString(),
      updated_at: new Date(now - 3 * dayMs).toISOString()
    },
    {
      id: 3,
      user_id: 1,
      title: 'Maintenance Schedule',
      content: 'Weekly maintenance scheduled for all portal systems. Gate sigils need re-energizing and protective wards require renewal.',
      is_private: 0,
      created_at: new Date(now - 1 * dayMs).toISOString(),
      updated_at: new Date(now - 1 * dayMs).toISOString()
    },
    {
      id: 4,
      user_id: 1,
      title: 'System Backup Complete',
      content: 'Automated backup of all gate configurations completed successfully. Backup stored in secure location with proper encryption.',
      is_private: 0,
      created_at: new Date(now - 6 * dayMs).toISOString(),
      updated_at: new Date(now - 6 * dayMs).toISOString()
    },
    {
      id: 5,
      user_id: 1,
      title: 'New Gatekeeper Training',
      content: 'Conducted training session for new gatekeepers. Covered basic portal management and emergency procedures.',
      is_private: 0,
      created_at: new Date(now - 7 * dayMs).toISOString(),
      updated_at: new Date(now - 7 * dayMs).toISOString()
    },
    {
      id: 6,
      user_id: 1,
      title: 'Emergency Protocol Review',
      content: 'Reviewed emergency shutdown procedures for all active gates. All systems operational and ready.',
      is_private: 1,
      created_at: new Date(now - 8 * dayMs).toISOString(),
      updated_at: new Date(now - 8 * dayMs).toISOString()
    },
    {
      id: 7,
      user_id: 1,
      title: 'Budget Planning Notes',
      content: 'Planning next quarter budget allocation for gate maintenance and new equipment. Need to prioritize critical repairs.',
      is_private: 1,
      created_at: new Date(now - 9 * dayMs).toISOString(),
      updated_at: new Date(now - 9 * dayMs).toISOString()
    },
    {
      id: 8,
      user_id: 1,
      title: 'Staff Meeting Minutes',
      content: 'Monthly staff meeting completed. Discussed upcoming maintenance schedule and new security protocols.',
      is_private: 0,
      created_at: new Date(now - 10 * dayMs).toISOString(),
      updated_at: new Date(now - 10 * dayMs).toISOString()
    },
    {
      id: 9,
      user_id: 1,
      title: 'Equipment Inventory',
      content: 'Completed inventory of all gate maintenance equipment. Several items need replacement or repair.',
      is_private: 0,
      created_at: new Date(now - 11 * dayMs).toISOString(),
      updated_at: new Date(now - 11 * dayMs).toISOString()
    },
    {
      id: 10,
      user_id: 1,
      title: 'System Status',
      content: 'All gate systems operational. Monitoring continues as scheduled.',
      is_private: 0,
      created_at: new Date(now - 12 * dayMs).toISOString(),
      updated_at: new Date(now - 12 * dayMs).toISOString()
    }
  ];
}

export function generateRandomNotes(totalNotes = 200) {
  const flag = readFlag();
  const flagPosition = Math.floor(Math.random() * totalNotes) + 1;
  
  console.log(`🎃 Generating ${totalNotes} notes...`);
  
  const noteTypes = [
    'Gate Inspection Log',
    'Security Audit Report',
    'System Performance Review',
    'Training Documentation',
    'Equipment Status Update',
    'Portal Configuration Log',
    'Emergency Response Record',
    'Team Meeting Summary',
    'Budget Allocation Plan',
    'Research Findings',
    'Field Survey Results',
    'Ritual Procedure Notes',
    'Seal Verification Report',
    'Navigation Protocol Update',
    'Realm Survey Data',
    'Historical Analysis',
    'Stability Monitoring Log',
    'Equipment Test Results',
    'Safety Compliance Check',
    'Administrative Notice'
  ];
  
  const contentTemplates = [
    'Completed routine inspection. All gates functioning within normal parameters. Minor adjustments made to threshold calibration.',
    'Security audit completed successfully. No vulnerabilities detected in current configuration. Recommend quarterly reviews.',
    'System performance monitored over 24-hour period. Response times normal. No anomalies detected.',
    'Training session completed with all participants. Covered emergency procedures and basic troubleshooting.',
    'Equipment inventory updated. All items accounted for. Maintenance scheduled for next quarter.',
    'Portal configuration adjusted for optimal stability. Changes logged and documented per protocol.',
    'Emergency response drill conducted. Team performance satisfactory. Areas for improvement identified.',
    'Team meeting held to discuss ongoing projects. Action items assigned and deadlines set.',
    'Budget reviewed and allocations approved for upcoming maintenance cycle. Funds secured.',
    'Research into gate mechanics progressing. New insights documented for further analysis.',
    'Field survey conducted across multiple locations. Data collected and ready for processing.',
    'Ritual procedures performed according to ancient protocols. Seals reinforced successfully.',
    'Verification checks completed on all active seals. Integrity confirmed across all monitored points.',
    'Navigation protocols updated to reflect recent changes in gate network topology.',
    'Realm survey expanded to new territories. Preliminary data shows interesting patterns.',
    'Historical documents analyzed. Connections found between ancient texts and current practices.',
    'Stability monitoring shows fluctuations within acceptable ranges. Continuous observation maintained.',
    'Equipment testing phase completed. All units passed specifications. Ready for deployment.',
    'Safety inspection conducted per regulations. Full compliance achieved. Certificate renewed.',
    'Administrative tasks completed. Documentation filed and archived according to policy.'
  ];
  
  const notes = [];
  
  for (let i = 1; i <= totalNotes; i++) {
    if (i === flagPosition) {
      notes.push({
        id: 10 + i,
        user_id: 1,
        title: 'Critical System Configuration',
        content: flag,
        is_private: 1,
        created_at: new Date(Date.now() - Math.floor(Math.random() * 30 + 1) * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - Math.floor(Math.random() * 30 + 1) * 24 * 60 * 60 * 1000).toISOString()
      });
    } else {
      const noteType = noteTypes[Math.floor(Math.random() * noteTypes.length)];
      const content = contentTemplates[Math.floor(Math.random() * contentTemplates.length)];
      const userId = Math.floor(Math.random() * 3) + 1; // Only users 1, 2, 3 (admin, mira, keeper)
      const isPrivate = Math.floor(Math.random() * 2);
      const daysAgo = Math.floor(Math.random() * 365) + 1;
      
      notes.push({
        id: 10 + i,
        user_id: userId,
        title: noteType,
        content: content,
        is_private: isPrivate,
        created_at: new Date(Date.now() - daysAgo * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - daysAgo * 24 * 60 * 60 * 1000).toISOString()
      });
    }
  }
  
  return notes;
}

