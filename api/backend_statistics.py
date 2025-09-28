# backend/app/statistics.py
import math
from scipy import stats
from typing import Tuple

def calculate_z_test(clicks_a: int, impressions_a: int, 
                    clicks_b: int, impressions_b: int) -> Tuple[float, float, Tuple[float, float], Tuple[float, float]]:
    """
    Calculate two-proportion z-test for CTR comparison
    
    Returns:
        z_statistic: Z test statistic
        p_value: Two-tailed p-value
        ci_a: 95% confidence interval for variant A
        ci_b: 95% confidence interval for variant B
    """
    if impressions_a == 0 or impressions_b == 0:
        return 0.0, 1.0, (0.0, 0.0), (0.0, 0.0)
    
    # Calculate proportions
    p1 = clicks_a / impressions_a
    p2 = clicks_b / impressions_b
    
    # Calculate pooled proportion
    n1 = impressions_a
    n2 = impressions_b
    p_pool = (clicks_a + clicks_b) / (impressions_a + impressions_b)
    
    # Calculate standard error
    se = math.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
    
    # Avoid division by zero
    if se == 0:
        return 0.0, 1.0, (p1, p1), (p2, p2)
    
    # Calculate z-statistic
    z_stat = (p1 - p2) / se
    
    # Calculate p-value (two-tailed)
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
    
    # Calculate 95% confidence intervals
    z_critical = 1.96  # 95% confidence level
    
    # CI for variant A
    se_a = math.sqrt(p1 * (1 - p1) / n1)
    ci_a = (
        max(0, p1 - z_critical * se_a),
        min(1, p1 + z_critical * se_a)
    )
    
    # CI for variant B
    se_b = math.sqrt(p2 * (1 - p2) / n2)
    ci_b = (
        max(0, p2 - z_critical * se_b),
        min(1, p2 + z_critical * se_b)
    )
    
    return z_stat, p_value, ci_a, ci_b

def calculate_like_rate_test(likes_a: int, views_a: int,
                           likes_b: int, views_b: int) -> Tuple[float, float, Tuple[float, float], Tuple[float, float]]:
    """
    Calculate two-proportion z-test for like rate comparison
    Similar to CTR test but for likes/views ratio
    """
    return calculate_z_test(likes_a, views_a, likes_b, views_b)

def check_stop_conditions(experiment_data: dict, stop_rules: dict) -> bool:
    """
    Check if experiment should be stopped based on stop rules
    
    Args:
        experiment_data: Current experiment metrics
        stop_rules: Dictionary with stopping conditions
    
    Returns:
        True if experiment should be stopped
    """
    if not stop_rules:
        return False
    
    # Check minimum samples
    min_samples = stop_rules.get('min_samples')
    if min_samples:
        total_samples = sum(variant.get('impressions', 0) for variant in experiment_data.get('variants', []))
        if total_samples < min_samples:
            return False
    
    # Check maximum hours
    max_hours = stop_rules.get('max_hours')
    if max_hours:
        # This would need start time from experiment
        # For now, assume this is checked externally
        pass
    
    # Check p-value threshold
    p_threshold = stop_rules.get('pvalue', 0.05)
    statistical_results = experiment_data.get('statistical_results')
    if statistical_results and statistical_results.get('p_value', 1.0) < p_threshold:
        return True
    
    return False