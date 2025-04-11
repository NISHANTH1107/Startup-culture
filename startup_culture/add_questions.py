import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'startup_culture.settings')
django.setup()

from career_site.models import Question  # Replace 'your_app' with your actual app name

# List of all 70 questions
questions = [
    {
        'text': 'At a party do you:',
        'option_a': 'Interact with many, including strangers',
        'option_b': 'Interact with a few, known to you',
        'order': 1
    },
    {
        'text': 'Are you more:',
        'option_a': 'Realistic than speculative',
        'option_b': 'Speculative than realistic',
        'order': 2
    },
    {
        'text': 'Is it worse to:',
        'option_a': 'Have your "head in the clouds"',
        'option_b': 'Be "in a rut"',
        'order': 3
    },
    {
        'text': 'Are you more impressed by:',
        'option_a': 'Principles',
        'option_b': 'Emotions',
        'order': 4
    },
    {
        'text': 'Are more drawn toward the:',
        'option_a': 'Convincing',
        'option_b': 'Touching',
        'order': 5
    },
    {
        'text': 'Do you prefer to work:',
        'option_a': 'To deadlines',
        'option_b': 'Just "whenever"',
        'order': 6
    },
    {
        'text': 'Do you tend to choose:',
        'option_a': 'Rather carefully',
        'option_b': 'Somewhat impulsively',
        'order': 7
    },
    {
        'text': 'At parties do you:',
        'option_a': 'Stay late, with increasing energy',
        'option_b': 'Leave early with decreased energy',
        'order': 8
    },
    {
        'text': 'Are you more attracted to:',
        'option_a': 'Sensible people',
        'option_b': 'Imaginative people',
        'order': 9
    },
    {
        'text': 'Are you more interested in:',
        'option_a': 'What is actual',
        'option_b': 'What is possible',
        'order': 10
    },
    {
        'text': 'In judging others are you more swayed by:',
        'option_a': 'Laws than circumstances',
        'option_b': 'Circumstances than laws',
        'order': 11
    },
    {
        'text': 'In approaching others is your inclination to be somewhat:',
        'option_a': 'Objective',
        'option_b': 'Personal',
        'order': 12
    },
    {
        'text': 'Are you more:',
        'option_a': 'Punctual',
        'option_b': 'Leisurely',
        'order': 13
    },
    {
        'text': 'Does it bother you more having things:',
        'option_a': 'Incomplete',
        'option_b': 'Completed',
        'order': 14
    },
    {
        'text': 'In your social groups do you:',
        'option_a': 'Keep abreast of other\'s happenings',
        'option_b': 'Get behind on the news',
        'order': 15
    },
    {
        'text': 'In doing ordinary things are you more likely to:',
        'option_a': 'Do it the usual way',
        'option_b': 'Do it your own way',
        'order': 16
    },
    {
        'text': 'Writers should:',
        'option_a': '"Say what they mean and mean what they say"',
        'option_b': 'Express things more by use of analogy',
        'order': 17
    },
    {
        'text': 'Which appeals to you more:',
        'option_a': 'Consistency of thought',
        'option_b': 'Harmonious human relationships',
        'order': 18
    },
    {
        'text': 'Are you more comfortable in making:',
        'option_a': 'Logical judgments',
        'option_b': 'Value judgments',
        'order': 19
    },
    {
        'text': 'Do you want things:',
        'option_a': 'Settled and decided',
        'option_b': 'Unsettled and undecided',
        'order': 20
    },
    {
        'text': 'Would you say you are more:',
        'option_a': 'Serious and determined',
        'option_b': 'Easy-going',
        'order': 21
    },
    {
        'text': 'In phoning do you:',
        'option_a': 'Rarely question that it will all be said',
        'option_b': 'Rehearse what you\'ll say',
        'order': 22
    },
    {
        'text': 'Facts:',
        'option_a': '"Speak for themselves"',
        'option_b': 'Illustrate principles',
        'order': 23
    },
    {
        'text': 'Are visionaries:',
        'option_a': 'somewhat annoying',
        'option_b': 'rather fascinating',
        'order': 24
    },
    {
        'text': 'Are you more often:',
        'option_a': 'a cool-headed person',
        'option_b': 'a warm-hearted person',
        'order': 25
    },
    {
        'text': 'Is it worse to be:',
        'option_a': 'unjust',
        'option_b': 'merciless',
        'order': 26
    },
    {
        'text': 'Should one usually let events occur:',
        'option_a': 'by careful selection and choice',
        'option_b': 'randomly and by chance',
        'order': 27
    },
    {
        'text': 'Do you feel better about:',
        'option_a': 'having purchased',
        'option_b': 'having the option to buy',
        'order': 28
    },
    {
        'text': 'In company do you:',
        'option_a': 'initiate conversation',
        'option_b': 'wait to be approached',
        'order': 29
    },
    {
        'text': 'Common sense is:',
        'option_a': 'rarely questionable',
        'option_b': 'frequently questionable',
        'order': 30
    },
    {
        'text': 'Children often do not:',
        'option_a': 'make themselves useful enough',
        'option_b': 'exercise their fantasy enough',
        'order': 31
    },
    {
        'text': 'In making decisions do you feel more comfortable with:',
        'option_a': 'standards',
        'option_b': 'feelings',
        'order': 32
    },
    {
        'text': 'Are you more:',
        'option_a': 'firm than gentle',
        'option_b': 'gentle than firm',
        'order': 33
    },
    {
        'text': 'Which is more admirable:',
        'option_a': 'the ability to organize and be methodical',
        'option_b': 'the ability to adapt and make do',
        'order': 34
    },
    {
        'text': 'Do you put more value on:',
        'option_a': 'infinite',
        'option_b': 'open-minded',
        'order': 35
    },
    {
        'text': 'Does new and non-routine interaction with others:',
        'option_a': 'stimulate and energize you',
        'option_b': 'tax your reserves',
        'order': 36
    },
    {
        'text': 'Are you more frequently:',
        'option_a': 'a practical sort of person',
        'option_b': 'a fanciful sort of person',
        'order': 37
    },
    {
        'text': 'Are you more likely to:',
        'option_a': 'see how others are useful',
        'option_b': 'see how others see',
        'order': 38
    },
    {
        'text': 'Which is more satisfying:',
        'option_a': 'to discuss an issue thoroughly',
        'option_b': 'to arrive at agreement on an issue',
        'order': 39
    },
    {
        'text': 'Which rules you more:',
        'option_a': 'your head',
        'option_b': 'your heart',
        'order': 40
    },
    {
        'text': 'Are you more comfortable with work that is:',
        'option_a': 'contracted',
        'option_b': 'done on a casual basis',
        'order': 41
    },
    {
        'text': 'Do you tend to look for:',
        'option_a': 'the orderly',
        'option_b': 'whatever turns up',
        'order': 42
    },
    {
        'text': 'Do you prefer:',
        'option_a': 'many friends with brief contact',
        'option_b': 'a few friends with more lengthy contact',
        'order': 43
    },
    {
        'text': 'Do you go more by:',
        'option_a': 'facts',
        'option_b': 'principles',
        'order': 44
    },
    {
        'text': 'Are you more interested in:',
        'option_a': 'production and distribution',
        'option_b': 'design and research',
        'order': 45
    },
    {
        'text': 'Which is more of a compliment:',
        'option_a': '"There is a very logical person."',
        'option_b': '"There is a very sentimental person."',
        'order': 46
    },
    {
        'text': 'Do you value in yourself more that you are:',
        'option_a': 'unwavering',
        'option_b': 'devoted',
        'order': 47
    },
    {
        'text': 'Do you more often prefer the',
        'option_a': 'final and unalterable statement',
        'option_b': 'tentative and preliminary statement',
        'order': 48
    },
    {
        'text': 'Are you more comfortable:',
        'option_a': 'after a decision',
        'option_b': 'before a decision',
        'order': 49
    },
    {
        'text': 'Do you:',
        'option_a': 'speak easily and at length with strangers',
        'option_b': 'find little to say to strangers',
        'order': 50
    },
    {
        'text': 'Are you more likely to trust your:',
        'option_a': 'experience',
        'option_b': 'hunch',
        'order': 51
    },
    {
        'text': 'Do you feel:',
        'option_a': 'more practical than ingenious',
        'option_b': 'more ingenious than practical',
        'order': 52
    },
    {
        'text': 'Which person is more to be complimented – one of:',
        'option_a': 'clear reason',
        'option_b': 'strong feeling',
        'order': 53
    },
    {
        'text': 'Are you inclined more to be:',
        'option_a': 'fair-minded',
        'option_b': 'sympathetic',
        'order': 54
    },
    {
        'text': 'Is it preferable mostly to:',
        'option_a': 'make sure things are arranged',
        'option_b': 'just let things happen',
        'order': 55
    },
    {
        'text': 'In relationships should most things be:',
        'option_a': 're-negotiable',
        'option_b': 'random and circumstantial',
        'order': 56
    },
    {
        'text': 'When the phone rings do you:',
        'option_a': 'hasten to get to it first',
        'option_b': 'hope someone else will answer',
        'order': 57
    },
    {
        'text': 'Do you prize more in yourself:',
        'option_a': 'a strong sense of reality',
        'option_b': 'a vivid imagination',
        'order': 58
    },
    {
        'text': 'Are you drawn more to:',
        'option_a': 'fundamentals',
        'option_b': 'overtones',
        'order': 59
    },
    {
        'text': 'Which seems the greater error:',
        'option_a': 'to be too passionate',
        'option_b': 'to be too objective',
        'order': 60
    },
    {
        'text': 'Do you see yourself as basically:',
        'option_a': 'hard-headed',
        'option_b': 'soft-hearted',
        'order': 61
    },
    {
        'text': 'Which situation appeals to you more:',
        'option_a': 'the structured and scheduled',
        'option_b': 'the unstructured and unscheduled',
        'order': 62
    },
    {
        'text': 'Are you a person that is more:',
        'option_a': 'routinized than whimsical',
        'option_b': 'whimsical than routinized',
        'order': 63
    },
    {
        'text': 'Are you more inclined to be:',
        'option_a': 'easy to approach',
        'option_b': 'somewhat reserved',
        'order': 64
    },
    {
        'text': 'In writings do you prefer:',
        'option_a': 'the more literal',
        'option_b': 'the more figurative',
        'order': 65
    },
    {
        'text': 'Is it harder for you to:',
        'option_a': 'identify with others',
        'option_b': 'utilize others',
        'order': 66
    },
    {
        'text': 'Which do you wish more for yourself:',
        'option_a': 'clarity of reason',
        'option_b': 'strength of compassion',
        'order': 67
    },
    {
        'text': 'Which is the greater fault:',
        'option_a': 'being indiscriminate',
        'option_b': 'being critical',
        'order': 68
    },
    {
        'text': 'Do you prefer the:',
        'option_a': 'planned event',
        'option_b': 'unplanned event',
        'order': 69
    },
    {
        'text': 'Do you tend to be more:',
        'option_a': 'deliberate than spontaneous',
        'option_b': 'spontaneous than deliberate',
        'order': 70
    },
]

# Add questions to database
for q in questions:
    question = Question.objects.create(
        text=q['text'],
        option_a=q['option_a'],
        option_b=q['option_b'],
        order=q['order']
    )
    print(f"Added question {question.order}: {question.text[:50]}...")

print("All questions have been added to the database.")