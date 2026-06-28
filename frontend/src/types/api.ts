export interface UploadResponse {
  project_id: number;
  status: string;
  files_processed: number;
}

export interface AnalysisSummary {
  total_files: number;
  total_classes: number;
  total_methods: number;
  total_dependencies: number;
}

export interface ClassAnalysis {
  name: string;
  file: string;
}

export interface MethodAnalysis {
  name: string;
  class: string;
  return_type: string | null;
}

export interface DependencyAnalysis {
  dependency: string;
  technology: string;
  category: string;
  risk_level: string;
  recommendation: string;
}

export interface ProjectAnalysisResponse {
  project_id: number;
  project_name: string;
  summary: AnalysisSummary;
  classes: ClassAnalysis[];
  methods: MethodAnalysis[];
  dependencies: DependencyAnalysis[];
}

export interface ArchitectureComponent {
  name: string;
  responsibility: string;
  classes: string[];
}

export interface ArchitectureSummary {
  components: ArchitectureComponent[];
}

export interface BusinessCapability {
  name: string;
  description: string;
}

export interface BusinessCapabilities {
  capabilities: BusinessCapability[];
}

export interface ArchitectureReport {
  application_overview: string;
  architecture_summary: string;
  components: Array<{ name: string; responsibility: string }>;
  business_capabilities: BusinessCapability[];
  technology_summary: string;
  technical_risks: string[];
  modernization_opportunities: string[];
}

export interface CodeAnalysis {
  summary: string;
  detected_components: string[];
}

export interface DependencyAnalysisResult {
  total_dependencies: number;
  high_risk_dependencies: Array<{
    dependency: string;
    technology: string;
    risk_level: string;
  }>;
}

export interface RiskAnalysis {
  overall_risk: string;
  reason: string;
}

export interface ModernizationPlan {
  architecture_assessment?: string;
  key_risks?: string[];
  recommended_steps?: string[];
  target_architecture?: string;
  summary?: string;
  recommendations?: string[];
}

export interface CodeModernizationOpportunity {
  component: string;
  legacy_technology_or_pattern: string;
  recommended_approach: string;
  justification: string;
  implementation_strategy: string;
  example_modernized_code: string;
  replaces: string;
  migration_considerations: string[];
  migration_risks: string[];
  enterprise_references: string[];
}

export interface CodeModernization {
  opportunities: CodeModernizationOpportunity[];
}

export interface ModernizationPlanResponse {
  project_id: number;
  classes: Array<{ name: string; file: string; package: string | null }>;
  methods: Array<{ name: string; class: string; return_type: string | null }>;
  dependencies: Array<{
    dependency: string;
    technology: string;
    risk_level: string;
  }>;
  code_analysis: CodeAnalysis;
  dependency_analysis: DependencyAnalysisResult;
  risk_analysis: RiskAnalysis;
  architecture_summary: ArchitectureSummary;
  business_capabilities: BusinessCapabilities;
  architecture_report: ArchitectureReport;
  modernization_plan: ModernizationPlan;
  code_modernization: CodeModernization;
}

export interface ApiError {
  detail: string;
}
