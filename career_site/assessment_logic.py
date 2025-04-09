from .models import Assessment, PersonalityResult
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

def split_into_sets(binary_list):
    """Splits binary answers into groups for personality dimension calculation."""
    try:
        # Handle the list if there are exactly 70 items (10 groups of 7)
        if len(binary_list) == 70:
            inter = [binary_list[i:i + 7] for i in range(0, len(binary_list), 7)]
            return [[inter[j][i] for j in range(len(inter))] for i in range(len(inter[0]))]
        
        # Fallback for non-standard question counts
        return [[binary_list[j] for j in range(i, len(binary_list), 7) if j < len(binary_list)] 
               for i in range(7)]
    
    except Exception as e:
        logger.error(f"Error splitting binary list: {str(e)}")
        # Return empty groups if processing fails
        return [[] for _ in range(7)]

def calculate_personality_type(assessment):
    """
    Calculates personality type from assessment answers.
    Returns PersonalityResult instance or None if calculation fails.
    """
    try:
        # Validate assessment exists and has answers
        if not isinstance(assessment, Assessment):
            raise ValueError("Invalid assessment object")
            
        answers = assessment.answers.all().order_by('question__order')
        if not answers.exists():
            logger.warning(f"No answers found for assessment {assessment.id}")
            return None

        # Convert answers to binary list
        binary_list = [int(answer.choice) for answer in answers]
        
        # Split into personality dimension groups
        split_data = split_into_sets(binary_list)
        
        # Calculate scores for each dimension
        assessment_score = [(group.count(0), group.count(1)) for group in split_data]
        
        # Handle case where we don't have exactly 7 dimensions
        if len(assessment_score) != 7:
            logger.warning(f"Unexpected number of dimensions: {len(assessment_score)}")
            # Pad with zeros if needed
            assessment_score = assessment_score + [(0, 0)] * (7 - len(assessment_score))
            assessment_score = assessment_score[:7]  # Ensure exactly 7 dimensions

        # Combine scores for MBTI dimensions
        final_score = [
            assessment_score[0],  # E/I
            (assessment_score[1][0] + assessment_score[2][0],  # S
             assessment_score[1][1] + assessment_score[2][1]), # N
            (assessment_score[3][0] + assessment_score[4][0],  # T
             assessment_score[3][1] + assessment_score[4][1]), # F
            (assessment_score[5][0] + assessment_score[6][0],  # J
             assessment_score[5][1] + assessment_score[6][1])  # P
        ]

        # Determine personality type
        personality_type = ''.join([
            'E' if final_score[0][1] > final_score[0][0] else 'I',
            'S' if final_score[1][0] > final_score[1][1] else 'N',
            'T' if final_score[2][0] > final_score[2][1] else 'F',
            'J' if final_score[3][0] > final_score[3][1] else 'P'
        ])

        # Calculate relative scores (0-100 scale showing dominance)
        ei_score = (final_score[0][1] / (final_score[0][0] + final_score[0][1])) * 100 if (final_score[0][0] + final_score[0][1]) > 0 else 50
        sn_score = (final_score[1] / (final_score[1] + final_score[2])) * 100 if (final_score[1] + final_score[2]) > 0 else 50
        tf_score = (final_score[3] / (final_score[3] + final_score[4])) * 100 if (final_score[3] + final_score[4]) > 0 else 50
        jp_score = (final_score[5] / (final_score[5] + final_score[6])) * 100 if (final_score[5] + final_score[6]) > 0 else 50

        # Create or update the result
        result, created = PersonalityResult.objects.update_or_create(
            assessment=assessment,
            defaults={
                'personality_type': personality_type,
                'ei_score': round(ei_score),
                'sn_score': round(sn_score),
                'tf_score': round(tf_score),
                'jp_score': round(jp_score),
                # Store raw scores for debugging
                'raw_e_score': final_score[0][1],
                'raw_i_score': final_score[0][0],
                'raw_s_score': final_score[1],
                'raw_n_score': final_score[2],
                'raw_t_score': final_score[3],
                'raw_f_score': final_score[4],
                'raw_j_score': final_score[5],
                'raw_p_score': final_score[6],
            }
        )
        
        return result

    except Exception as e:
        logger.error(f"Error calculating personality type for assessment {assessment.id}: {str(e)}")
        return None