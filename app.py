"""
Flask web demo for nlcli v1.2.0 Enhanced Partial Matching Pipeline
"""

import json
import time
from flask import Flask, render_template, request, jsonify
from nlcli.pipeline.ai_translator import AITranslator
from nlcli.pipeline.shell_adapter import ShellAdapter
from nlcli.pipeline.command_filter import CommandFilter
from nlcli.pipeline.pattern_engine import PatternEngine
from nlcli.pipeline.fuzzy_engine import AdvancedFuzzyEngine
from nlcli.pipeline.semantic_matcher import SemanticMatcher

app = Flask(__name__)

# Initialize pipeline components
translator = AITranslator()
shell_adapter = ShellAdapter()
command_filter = CommandFilter()
pattern_engine = PatternEngine()
fuzzy_engine = AdvancedFuzzyEngine()
semantic_matcher = SemanticMatcher()

@app.route('/')
def index():
    """Main demo page"""
    return render_template('index.html')

@app.route('/api/translate', methods=['POST'])
def translate_command():
    """API endpoint for command translation with pipeline breakdown"""
    data = request.get_json()
    natural_input = data.get('input', '').strip()
    
    if not natural_input:
        return jsonify({'error': 'No input provided'}), 400
    
    # Track pipeline processing
    pipeline_results = {
        'input': natural_input,
        'pipeline_breakdown': [],
        'final_result': None,
        'total_time': 0
    }
    
    start_time = time.time()
    
    try:
        # Level 1: Shell Adapter - Context
        level1_start = time.time()
        context = shell_adapter.get_pipeline_metadata(natural_input)
        level1_time = (time.time() - level1_start) * 1000
        
        pipeline_results['pipeline_breakdown'].append({
            'level': 1,
            'name': 'Shell Adapter',
            'description': 'Context generation',
            'time_ms': round(level1_time, 3),
            'result': 'Context generated',
            'details': f"Platform: {context.get('platform', 'unknown')}"
        })
        
        # Level 2: Command Filter - Direct commands
        level2_start = time.time()
        level2_result = command_filter.get_pipeline_metadata(natural_input)
        level2_time = (time.time() - level2_start) * 1000
        
        if level2_result:
            pipeline_results['final_result'] = level2_result
            pipeline_results['pipeline_breakdown'].append({
                'level': 2,
                'name': 'Command Filter',
                'description': 'Direct command match',
                'time_ms': round(level2_time, 3),
                'result': 'MATCH FOUND',
                'details': f"Command: {level2_result['command']}"
            })
        else:
            pipeline_results['pipeline_breakdown'].append({
                'level': 2,
                'name': 'Command Filter',
                'description': 'Direct command match',
                'time_ms': round(level2_time, 3),
                'result': 'No match',
                'details': 'Continuing to next level'
            })
            
            # Level 3: Pattern Engine
            level3_start = time.time()
            level3_result = pattern_engine.get_pipeline_metadata(natural_input, context)
            level3_time = (time.time() - level3_start) * 1000
            
            if level3_result:
                pipeline_results['final_result'] = level3_result
                pipeline_results['pipeline_breakdown'].append({
                    'level': 3,
                    'name': 'Pattern Engine',
                    'description': 'Semantic patterns',
                    'time_ms': round(level3_time, 3),
                    'result': 'MATCH FOUND',
                    'details': f"Pattern: {level3_result.get('pattern_type', 'semantic')}"
                })
            else:
                pipeline_results['pipeline_breakdown'].append({
                    'level': 3,
                    'name': 'Pattern Engine',
                    'description': 'Semantic patterns',
                    'time_ms': round(level3_time, 3),
                    'result': 'No match',
                    'details': 'Continuing to next level'
                })
                
                # Level 4: Fuzzy Engine
                level4_start = time.time()
                level4_result = fuzzy_engine.get_pipeline_metadata(natural_input, context)
                level4_time = (time.time() - level4_start) * 1000
                
                if level4_result:
                    pipeline_results['final_result'] = level4_result
                    pipeline_results['pipeline_breakdown'].append({
                        'level': 4,
                        'name': 'Fuzzy Engine',
                        'description': 'Typo correction',
                        'time_ms': round(level4_time, 3),
                        'result': 'MATCH FOUND',
                        'details': f"Corrected: {level4_result.get('match_type', 'fuzzy')}"
                    })
                else:
                    pipeline_results['pipeline_breakdown'].append({
                        'level': 4,
                        'name': 'Fuzzy Engine',
                        'description': 'Typo correction',
                        'time_ms': round(level4_time, 3),
                        'result': 'No match',
                        'details': 'Continuing to next level'
                    })
                    
                    # Level 5: Semantic Intelligence Hub
                    level5_start = time.time()
                    level5_result = semantic_matcher.get_pipeline_metadata(natural_input, context)
                    level5_time = (time.time() - level5_start) * 1000
                    
                    if level5_result:
                        pipeline_results['final_result'] = level5_result
                        pipeline_results['pipeline_breakdown'].append({
                            'level': 5,
                            'name': 'Semantic Intelligence Hub',
                            'description': 'Enhanced partial matching',
                            'time_ms': round(level5_time, 3),
                            'result': 'MATCH FOUND',
                            'details': f"Confidence: {level5_result.get('confidence', 'N/A')}%"
                        })
                    else:
                        pipeline_results['pipeline_breakdown'].append({
                            'level': 5,
                            'name': 'Semantic Intelligence Hub',
                            'description': 'Enhanced partial matching',
                            'time_ms': round(level5_time, 3),
                            'result': 'No match',
                            'details': 'Would fallback to AI (Level 6)'
                        })
        
        # Calculate total time
        pipeline_results['total_time'] = round((time.time() - start_time) * 1000, 3)
        
        # Format final result for display
        if pipeline_results['final_result']:
            result = pipeline_results['final_result']
            pipeline_results['command'] = result.get('command', 'No command')
            pipeline_results['explanation'] = result.get('explanation', 'No explanation')
            pipeline_results['confidence'] = result.get('confidence', 0)
            pipeline_results['source'] = result.get('source', 'unknown')
            pipeline_results['success'] = True
        else:
            pipeline_results['command'] = 'No translation found'
            pipeline_results['explanation'] = 'Would require AI translation (Level 6)'
            pipeline_results['confidence'] = 0
            pipeline_results['source'] = 'none'
            pipeline_results['success'] = False
            
        return jsonify(pipeline_results)
        
    except Exception as e:
        return jsonify({
            'error': f'Translation failed: {str(e)}',
            'pipeline_breakdown': pipeline_results.get('pipeline_breakdown', []),
            'total_time': round((time.time() - start_time) * 1000, 3)
        }), 500

@app.route('/api/examples')
def get_examples():
    """Get example commands for demo"""
    examples = [
        {
            'category': 'Instant Recognition (Level 2)',
            'commands': [
                'ls', 'pwd', 'docker ps', 'git status', 'npm install'
            ]
        },
        {
            'category': 'Pattern Matching (Level 3)',
            'commands': [
                'list files', 'show directory', 'network status', 'find logs'
            ]
        },
        {
            'category': 'Typo Correction (Level 4)',
            'commands': [
                'lis files', 'shw directory', 'dok ps', 'gt status'
            ]
        },
        {
            'category': 'Semantic Intelligence (Level 5)',
            'commands': [
                'netwok status', 'shw all processes', 'lis hidden files'
            ]
        }
    ]
    return jsonify(examples)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)