from .models import Assessment, PersonalityResult
from django.core.exceptions import ObjectDoesNotExist
import logging
import numpy as np
import matplotlib.pyplot as plt
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

def calculate_personality_type(assessment):
    """
    Correctly calculates personality type with proper scoring
    """
    try:
        # Validate assessment exists and has answers
        if not isinstance(assessment, Assessment):
            raise ValueError("Invalid assessment object")
            
        answers = assessment.answers.all().order_by('question__order')
        if not answers.exists():
            logger.warning(f"No answers found for assessment {assessment.id}")
            return None

        # Convert answers to binary choices (0 for A, 1 for B)
        binary_answers = [int(answer.choice) for answer in answers]
        
        if len(binary_answers) != 70:
            logger.error(f"Expected 70 answers, got {len(binary_answers)}")
            return None

        # Group and transpose questions
        grouped = [binary_answers[i:i+7] for i in range(0, 70, 7)]
        columns = np.array(grouped).T.tolist()

        # Calculate raw scores
        e_score = columns[0].count(1)  # Col1 B answers
        i_score = columns[0].count(0)  # Col1 A answers
        
        s_score = columns[1].count(0) + columns[2].count(0)
        n_score = columns[1].count(1) + columns[2].count(1)
        
        t_score = columns[3].count(0) + columns[4].count(0)
        f_score = columns[3].count(1) + columns[4].count(1)
        
        j_score = columns[5].count(0) + columns[6].count(0)
        p_score = columns[5].count(1) + columns[6].count(1)

        # Calculate percentages
        def calculate_percentage(score1, score2):
            total = score1 + score2
            return int((score1 / total) * 100) if total else 50

        e_percent = calculate_percentage(e_score, i_score)
        i_percent = 100 - e_percent
        
        s_percent = calculate_percentage(s_score, n_score)
        n_percent = 100 - s_percent
        
        t_percent = calculate_percentage(t_score, f_score)
        f_percent = 100 - t_percent
        
        j_percent = calculate_percentage(j_score, p_score)
        p_percent = 100 - j_percent

        # Determine personality type
        personality_type = ''.join([
            'E' if e_score > i_score else 'I',
            'S' if s_score > n_score else 'N',
            'T' if t_score > f_score else 'F',
            'J' if j_score > p_score else 'P'
        ])

        # Get type data
        type_data = PersonalityResult.get_type_data().get(personality_type, {})
        
        # Create the result
        result = PersonalityResult.objects.create(
            assessment=assessment,
            type_code=personality_type,
            personality_type=personality_type,
            title=type_data.get('title', ''),
            description=type_data.get('description', ''),
            strengths=type_data.get('strengths', ''),
            growth_areas=type_data.get('growth_areas', ''),
            career_suggestions=type_data.get('career_suggestions', ''),
            relationships=type_data.get('relationships', ''),
            famous_examples=type_data.get('famous_examples', ''),
            banner_color=type_data.get('banner_color', '#D4AF37'),
            # Store raw scores
            raw_e_score=e_score,
            raw_i_score=i_score,
            raw_s_score=s_score,
            raw_n_score=n_score,
            raw_t_score=t_score,
            raw_f_score=f_score,
            raw_j_score=j_score,
            raw_p_score=p_score,
            # Store percentage scores
            ei_score=e_percent,
            sn_score=s_percent,
            tf_score=t_percent,
            jp_score=j_percent
        )
        
        return result

    except Exception as e:
        logger.error(f"Error calculating personality type: {str(e)}", exc_info=True)
        return None
