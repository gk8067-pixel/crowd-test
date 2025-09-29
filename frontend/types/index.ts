export interface Survey {
  id: number;
  title: string;
  description?: string;
  creator_id: number;
  is_active: boolean;
  start_date?: string;
  end_date?: string;
  created_at: string;
  updated_at: string;
  questions?: Question[];
}

export interface Question {
  id: number;
  survey_id: number;
  question_text: string;
  question_type: 'text' | 'radio' | 'checkbox' | 'rating' | 'dropdown';
  is_required: boolean;
  order_index: number;
  options?: string[] | null;
  created_at: string;
  updated_at: string;
}

export interface Response {
  id: number;
  survey_id: number;
  user_id?: number;
  ip_address?: string;
  user_agent?: string;
  submitted_at: string;
  answers?: Answer[];
}

export interface Answer {
  id: number;
  response_id: number;
  question_id: number;
  answer_text?: string;
  answer_data?: any;
  created_at: string;
}

export interface SurveyStatistics {
  total_responses: number;
  completion_rate: number;
  average_time?: number;
  question_statistics: QuestionStatistics[];
}

export interface QuestionStatistics {
  question_id: number;
  question_text: string;
  question_type: string;
  response_count: number;
  statistics: any;
}

export interface SurveyFormData {
  title: string;
  description?: string;
  is_active: boolean;
  start_date?: string;
  end_date?: string;
}

export interface QuestionFormData {
  question_text: string;
  question_type: 'text' | 'radio' | 'checkbox' | 'rating' | 'dropdown';
  is_required: boolean;
  order_index: number;
  options?: string[];
}