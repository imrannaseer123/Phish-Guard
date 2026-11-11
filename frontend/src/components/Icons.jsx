import React from 'react';
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  BarChart3,
  BookOpen,
  Bot,
  Brain,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Clock,
  Cpu,
  Database,
  Download,
  ExternalLink,
  Eye,
  FileCode2,
  FileText,
  Filter,
  FlaskConical,
  GitBranch,
  Globe,
  GraduationCap,
  History,
  Home,
  Inbox,
  Info,
  KeyRound,
  Languages,
  Layers,
  Link2,
  Lock,
  LogOut,
  Mail,
  Menu,
  MessageSquare,
  Moon,
  Network,
  QrCode,
  RefreshCw,
  Scale,
  ScanSearch,
  Search,
  Send,
  Shield,
  ShieldAlert,
  ShieldCheck,
  SlidersHorizontal,
  Sun,
  Target,
  Trash2,
  TrendingDown,
  TrendingUp,
  Type,
  User,
  UserCheck,
  Waypoints,
  X,
  XCircle,
} from 'lucide-react';

export const Icon = {
  Activity,
  AlertCircle,
  AlertTriangle,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  BarChart3,
  BookOpen,
  Bot,
  Brain,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Clock,
  Cpu,
  Database,
  Download,
  ExternalLink,
  Eye,
  FileCode2,
  FileText,
  Filter,
  FlaskConical,
  GitBranch,
  Globe,
  GraduationCap,
  History,
  Home,
  Inbox,
  Info,
  KeyRound,
  Languages,
  Layers,
  Link2,
  Lock,
  LogOut,
  Mail,
  Menu,
  MessageSquare,
  Moon,
  Network,
  QrCode,
  RefreshCw,
  Scale,
  ScanSearch,
  Search,
  Send,
  Shield,
  ShieldAlert,
  ShieldCheck,
  SlidersHorizontal,
  Sun,
  Target,
  Trash2,
  TrendingDown,
  TrendingUp,
  Type,
  User,
  UserCheck,
  Waypoints,
  X,
  XCircle,
};

export function AnalyzerIcon({ name, size = 16, className = '' }) {
  const props = { size, strokeWidth: 1.5, className, 'aria-hidden': 'true' };
  switch (name) {
    case 'keyword':
      return <Type {...props} />;
    case 'url':
      return <Link2 {...props} />;
    case 'sender':
      return <User {...props} />;
    case 'urgency':
      return <Clock {...props} />;
    case 'structure':
      return <FileText {...props} />;
    case 'header_forensics':
      return <Network {...props} />;
    case 'threat_intel':
      return <Globe {...props} />;
    case 'ocr_analyzer':
      return <Eye {...props} />;
    case 'qr_analyzer':
    case 'qr_code':
      return <QrCode {...props} />;
    default:
      return <ScanSearch {...props} />;
  }
}

export function IntentIcon({ intent, size = 16, className = '' }) {
  const props = { size, strokeWidth: 1.5, className, 'aria-hidden': 'true' };
  switch (intent) {
    case 'Credential Harvesting':
      return <KeyRound {...props} />;
    case 'Financial Fraud':
      return <Scale {...props} />;
    case 'Malware Delivery':
      return <ShieldAlert {...props} />;
    case 'Identity Theft':
      return <UserCheck {...props} />;
    case 'Legitimate':
      return <ShieldCheck {...props} />;
    default:
      return <AlertCircle {...props} />;
  }
}

