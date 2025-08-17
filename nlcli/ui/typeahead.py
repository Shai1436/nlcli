"""
Typeahead autocomplete system for natural language CLI
Provides real-time command suggestions based on command history and patterns
"""

import re
import time
from typing import List, Optional, Tuple, Dict, Any
from difflib import SequenceMatcher
from ..storage.history_manager import HistoryManager
from ..utils.utils import setup_logging

logger = setup_logging()

class TypeaheadEngine:
    """Intelligent typeahead autocomplete engine with fuzzy matching and learning"""
    
    def __init__(self, history_manager: HistoryManager, ai_translator=None):
        self.history_manager = history_manager
        self.ai_translator = ai_translator  # For L1-L6 pipeline integration
        self._cache = {}
        self._cache_timestamp = 0
        self._cache_ttl = 60  # Cache for 60 seconds
        self._min_prefix_length = 2  # Minimum characters before suggesting
        self._max_suggestions = 5  # Maximum number of suggestions
        
        # Common command patterns for initial suggestions
        self.common_patterns = [
            "show files",
            "list directory",
            "check status",
            "run tests", 
            "start server",
            "install dependencies",
            "commit changes",
            "push changes",
            "pull latest",
            "create file",
            "delete file",
            "copy file",
            "move file",
            "find file",
            "search for",
            "change directory",
            "go to",
            "open in",
            "edit file",
            "view logs",
            "check processes",
            "kill process",
            "network status",
            "disk usage",
            "memory usage",
            "system info"
        ]
    
    def get_command_history(self, limit: int = 100) -> List[str]:
        """
        Get recent command history for autocomplete suggestions
        
        Args:
            limit: Maximum number of commands to retrieve
            
        Returns:
            List of recent natural language commands
        """
        try:
            # Get recent history entries
            history_entries = self.history_manager.get_recent_commands(limit=limit)
            
            # Extract unique natural language inputs
            commands = []
            seen = set()
            
            for entry in history_entries:
                natural_input = entry.get('natural_language', '').strip()
                if natural_input and natural_input.lower() not in seen:
                    commands.append(natural_input)
                    seen.add(natural_input.lower())
            
            return commands
            
        except Exception as e:
            logger.debug(f"Failed to get command history: {e}")
            return []
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings
        
        Args:
            text1: First text string
            text2: Second text string
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Use SequenceMatcher for fuzzy similarity
        matcher = SequenceMatcher(None, text1.lower(), text2.lower())
        return matcher.ratio()
    
    def prefix_match_score(self, prefix: str, candidate: str) -> float:
        """
        Calculate prefix match score with position weighting
        
        Args:
            prefix: Input prefix to match
            candidate: Candidate string to score
            
        Returns:
            Score between 0.0 and 1.0, higher for better matches
        """
        prefix_lower = prefix.lower()
        candidate_lower = candidate.lower()
        
        # Exact prefix match gets highest score
        if candidate_lower.startswith(prefix_lower):
            return 1.0
        
        # Word boundary matches get high score
        words = candidate_lower.split()
        for i, word in enumerate(words):
            if word.startswith(prefix_lower):
                # Earlier words get higher score
                position_weight = 1.0 - (i * 0.1)
                return max(0.7 * position_weight, 0.3)
        
        # Substring matches get medium score
        if prefix_lower in candidate_lower:
            # Position-based scoring for substring matches
            position = candidate_lower.find(prefix_lower)
            position_weight = 1.0 - (position / len(candidate_lower))
            return max(0.5 * position_weight, 0.2)
        
        # Fuzzy similarity as fallback
        similarity = self.calculate_similarity(prefix, candidate)
        if similarity > 0.6:
            return similarity * 0.4
        
        return 0.0
    
    def get_suggestions(self, prefix: str, max_results: int = None) -> List[Tuple[str, float]]:
        """
        Get autocomplete suggestions for the given prefix
        
        Args:
            prefix: Input prefix to complete
            max_results: Maximum number of suggestions to return
            
        Returns:
            List of (suggestion, confidence_score) tuples sorted by relevance
        """
        if len(prefix) < self._min_prefix_length:
            return []
        
        max_results = max_results if max_results is not None else self._max_suggestions
        
        # Check cache first
        cache_key = f"{prefix}:{max_results}"
        current_time = time.time()
        
        if (cache_key in self._cache and 
            current_time - self._cache_timestamp < self._cache_ttl):
            return self._cache[cache_key]
        
        # Get suggestions from L1-L6 pipeline if available
        pipeline_suggestions = self._get_pipeline_suggestions(prefix)
        
        # Get command history and common patterns
        history_commands = self.get_command_history()
        all_candidates = pipeline_suggestions + history_commands + self.common_patterns
        
        # Score all candidates
        scored_suggestions = []
        
        for candidate in all_candidates:
            if candidate and len(candidate) > len(prefix):
                score = self.prefix_match_score(prefix, candidate)
                if score > 0.1:  # Minimum threshold
                    scored_suggestions.append((candidate, score))
        
        # Sort by score (descending) and remove duplicates
        scored_suggestions.sort(key=lambda x: x[1], reverse=True)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        
        for suggestion, score in scored_suggestions:
            suggestion_lower = suggestion.lower()
            if suggestion_lower not in seen:
                unique_suggestions.append((suggestion, score))
                seen.add(suggestion_lower)
                
                if len(unique_suggestions) >= max_results:
                    break
        
        # Cache the results
        self._cache[cache_key] = unique_suggestions
        self._cache_timestamp = current_time
        
        return unique_suggestions
    
    def get_best_completion(self, prefix: str) -> Optional[str]:
        """
        Get the best autocomplete suggestion for the given prefix
        
        Args:
            prefix: Input prefix to complete
            
        Returns:
            Best completion string or None if no good match
        """
        suggestions = self.get_suggestions(prefix, max_results=1)
        
        if suggestions and suggestions[0][1] > 0.5:  # Confidence threshold
            return suggestions[0][0]
        
        return None
    
    def format_completion_display(self, prefix: str, completion: str) -> Tuple[str, str]:
        """
        Format completion for display with prefix and completion parts
        
        Args:
            prefix: User input prefix
            completion: Full completion string
            
        Returns:
            Tuple of (prefix_part, completion_part) for separate styling
        """
        if not completion or not completion.lower().startswith(prefix.lower()):
            return prefix, ""
        
        # Extract the completion part (what should be displayed in muted color)
        completion_part = completion[len(prefix):]
        return prefix, completion_part
    
    def update_suggestion_usage(self, used_suggestion: str, prefix: str):
        """
        Update usage statistics for suggestion learning
        
        Args:
            used_suggestion: The suggestion that was selected
            prefix: The prefix that led to this suggestion
        """
        # This would typically update a learning model or usage statistics
        # For now, we'll log the usage for future enhancement
        logger.debug(f"Suggestion used: '{used_suggestion}' from prefix '{prefix}'")
        
        # Future enhancement: Could store suggestion usage patterns
        # to improve future autocomplete relevance
    
    def clear_cache(self):
        """Clear the suggestion cache"""
        self._cache.clear()
        self._cache_timestamp = 0
    
    def _get_pipeline_suggestions(self, prefix: str) -> List[str]:
        """Get suggestions from L1-L6 performance pipeline"""
        suggestions = []
        
        if not self.ai_translator:
            return suggestions
        
        try:
            # Try L1: Enhanced Typo Correction
            if hasattr(self.ai_translator, 'shell_corrector'):
                corrected = self.ai_translator.shell_corrector.correct_typo(prefix)
                if corrected and corrected != prefix:
                    suggestions.append(corrected)
            
            # Try L2: Direct Command Filter  
            if hasattr(self.ai_translator, 'command_filter'):
                direct_result = self.ai_translator.command_filter.get_direct_command_result(prefix)
                if direct_result and 'natural_language' in direct_result:
                    suggestions.append(direct_result['natural_language'])
                
                # Get similar direct commands
                similar_commands = self.ai_translator.command_filter.get_similar_commands(prefix)
                suggestions.extend(similar_commands[:3])
            
            # Try L3: Enhanced Pattern Engine
            if hasattr(self.ai_translator, 'pattern_engine'):
                pattern_matches = self.ai_translator.pattern_engine.get_semantic_patterns()
                for pattern in pattern_matches[:3]:
                    if prefix.lower() in pattern.lower():
                        suggestions.append(pattern)
            
            # Try L4: Advanced Fuzzy Engine
            if hasattr(self.ai_translator, 'fuzzy_engine'):
                fuzzy_matches = self.ai_translator.fuzzy_engine.find_fuzzy_matches(prefix)
                suggestions.extend(fuzzy_matches[:3])
            
        except Exception as e:
            logger.debug(f"Pipeline suggestion error: {e}")
        
        return suggestions[:5]  # Limit pipeline suggestions
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics for debugging"""
        return {
            'cache_entries': len(self._cache),
            'cache_age_seconds': int(time.time() - self._cache_timestamp) if self._cache_timestamp else 0
        }


class TypeaheadDisplay:
    """Handles visual display of typeahead suggestions with proper styling"""
    
    def __init__(self):
        self.muted_style = '\033[37m'  # Muted white for completion text
        self.reset_style = '\033[0m'   # Reset to normal
        self.cursor_save = '\033[s'    # Save cursor position
        self.cursor_restore = '\033[u' # Restore cursor position
        self.clear_line = '\033[K'     # Clear from cursor to end of line
    
    def format_typeahead_line(self, prefix: str, completion_part: str) -> str:
        """
        Format a line with typeahead completion
        
        Args:
            prefix: User-typed prefix (normal color)
            completion_part: Autocomplete suggestion (muted color)
            
        Returns:
            Formatted string with appropriate styling
        """
        if not completion_part:
            return prefix
        
        return f"{prefix}{self.muted_style}{completion_part}{self.reset_style}"
    
    def display_inline_completion(self, prefix: str, completion: str) -> str:
        """
        Create inline completion display for real-time feedback
        
        Args:
            prefix: Current user input
            completion: Suggested completion
            
        Returns:
            Formatted display string
        """
        if not completion:
            return prefix
        
        # Format the completion display
        prefix_part, completion_part = self._extract_completion_part(prefix, completion)
        
        return self.format_typeahead_line(prefix_part, completion_part)
    
    def _extract_completion_part(self, prefix: str, completion: str) -> Tuple[str, str]:
        """Extract the part that should be shown as completion"""
        if completion.lower().startswith(prefix.lower()):
            return prefix, completion[len(prefix):]
        return prefix, ""
    
    def create_suggestion_menu(self, suggestions: List[Tuple[str, float]], max_display: int = 5) -> str:
        """
        Create a formatted menu of suggestions for display
        
        Args:
            suggestions: List of (suggestion, score) tuples
            max_display: Maximum number of suggestions to display
            
        Returns:
            Formatted menu string
        """
        if not suggestions:
            return ""
        
        menu_lines = []
        display_count = min(len(suggestions), max_display)
        
        for i in range(display_count):
            suggestion, score = suggestions[i]
            confidence_indicator = "●" if score > 0.8 else "○"
            menu_lines.append(f"  {confidence_indicator} {suggestion}")
        
        if len(suggestions) > max_display:
            menu_lines.append(f"  ... and {len(suggestions) - max_display} more")
        
        return "\n".join(menu_lines)


class TypeaheadController:
    """Main controller for typeahead functionality integration"""
    
    def __init__(self, history_manager: HistoryManager, ai_translator=None):
        self.engine = TypeaheadEngine(history_manager, ai_translator)
        self.display = TypeaheadDisplay()
        self.enabled = True
        self.show_suggestions_menu = False
    
    def get_completion_for_input(self, current_input: str) -> Optional[str]:
        """
        Get completion suggestion for current input
        
        Args:
            current_input: Current user input string
            
        Returns:
            Completion suggestion or None
        """
        if not self.enabled or len(current_input) < 2:
            return None
        
        return self.engine.get_best_completion(current_input)
    
    def format_input_with_completion(self, user_input: str, completion: Optional[str] = None) -> str:
        """
        Format user input with completion for display
        
        Args:
            user_input: Current user input
            completion: Suggested completion
            
        Returns:
            Formatted string for display
        """
        if not completion:
            completion = self.get_completion_for_input(user_input)
        
        if completion:
            return self.display.display_inline_completion(user_input, completion)
        
        return user_input
    
    def handle_completion_accept(self, current_input: str) -> str:
        """
        Handle user accepting a completion (right arrow key)
        
        Args:
            current_input: Current user input
            
        Returns:
            Full completed string
        """
        completion = self.get_completion_for_input(current_input)
        
        if completion:
            # Update usage statistics
            self.engine.update_suggestion_usage(completion, current_input)
            return completion
        
        return current_input
    
    def get_suggestions_menu(self, current_input: str) -> str:
        """
        Get formatted suggestions menu for display
        
        Args:
            current_input: Current user input
            
        Returns:
            Formatted suggestions menu
        """
        suggestions = self.engine.get_suggestions(current_input)
        return self.display.create_suggestion_menu(suggestions)
    
    def toggle_enabled(self):
        """Toggle typeahead on/off"""
        self.enabled = not self.enabled
        logger.debug(f"Typeahead {'enabled' if self.enabled else 'disabled'}")
    
    def clear_cache(self):
        """Clear typeahead cache"""
        self.engine.clear_cache()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get typeahead statistics"""
        return {
            'enabled': self.enabled,
            'engine_stats': self.engine.get_cache_stats()
        }