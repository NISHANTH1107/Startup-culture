import matplotlib
import matplotlib.pyplot as plt
import io
import base64
import seaborn as seaborn

def generate_personality_chart(personality_result):
    """
    Generate a radar chart visualizing the personality type scores.
    Returns a base64 encoded image string.
    """
    # Set the backend to Agg to avoid GUI issues
    matplotlib.use('Agg')
    
    # Categories and scores for the radar chart
    categories = ['Extraversion', 'Introversion', 'Sensing', 'Intuition', 
                 'Thinking', 'Feeling', 'Judging', 'Perceiving']
    
    scores = [
        personality_result.get_e_score(),
        personality_result.get_i_score(),
        personality_result.get_s_score(),
        personality_result.get_n_score(),
        personality_result.get_t_score(),
        personality_result.get_f_score(),
        personality_result.get_j_score(),
        personality_result.get_p_score()
    ]
    
    # The radar chart needs angles for each axis
    num_vars = len(categories)
    angles = [n / float(num_vars) * 2 * 3.14159 for n in range(num_vars)]
    angles += angles[:1]  # Complete the loop
    
    # Initialize the radar chart with custom styling
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    # Set background color
    fig.patch.set_facecolor('#f8f9fa')
    ax.set_facecolor('#f8f9fa')
    
    # Plot the data with improved styling
    scores += scores[:1]  # Complete the loop
    ax.plot(angles, scores, color='#D4AF37', linewidth=3, linestyle='solid', 
            marker='o', markersize=8, markerfacecolor='#D4AF37')
    ax.fill(angles, scores, color='#D4AF37', alpha=0.25)
    
    # Set the labels for each axis with better formatting
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=12, color='#333333')
    
    # Set the y-axis labels and grid
    ax.set_rlabel_position(30)
    plt.yticks([20, 40, 60, 80, 100], ["20", "40", "60", "80", "100"], 
               color='#666666', size=10)
    plt.ylim(0, 100)
    
    # Customize grid lines
    ax.grid(color='#aaaaaa', linestyle='--', linewidth=0.5, alpha=0.7)
    
    # Add title with personality type color coding
    plt.title(f"Personality Traits - {personality_result.type_code}", 
             size=16, y=1.1, color='#333333')
    
    # Add some padding around the plot
    plt.tight_layout(pad=3.0)
    
    # Save the plot to a bytes buffer with higher quality
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=120,
               facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    
    # Encode the image as base64
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    
    return image_base64