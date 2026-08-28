"""
AI Description Generator - Template-based Natural Language Generation
Converts rule triggers and detection context into human-readable descriptions.
"""

from typing import Dict, Optional
import time


class DescriptionGenerator:
    """
    Template-based NLG for generating natural language descriptions of detected anomalies.
    
    Uses structured templates with context substitution to create clear, consistent descriptions
    without hallucination risk. Optional LLM integration (Ollama) can be added later for more
    natural phrasing.
    """
    
    def __init__(self):
        """Initialize description generator with rule templates."""
        self.templates = {
            # Theft-indicative rules (Standard Priority)
            "Loitering in Shelf Zone": self._describe_loitering,
            "Repeated Shelf–Exit Movement": self._describe_shelf_exit,
            "Exit Without Checkout": self._describe_exit_no_checkout,
            
            # Violence/threat rules (High Priority) - to be implemented
            "Aggressive Pose Detection": self._describe_aggressive_pose,
            "Rapid Clustering/Dispersal": self._describe_clustering,
            "Elevated Object Detection": self._describe_elevated_object,
            "Group Freeze Posture": self._describe_freeze_posture,
        }
    
    def generate(self, rule_name: str, context: Dict) -> str:
        """
        Generate natural language description for a rule trigger.
        
        Args:
            rule_name: Name of triggered rule
            context: Dictionary with detection context:
                - person_id: Track ID
                - zone: Current zone name
                - dwell_time: Time spent in zone (seconds)
                - camera_id: Camera identifier
                - timestamp: Detection timestamp
                - pose_flags: Optional pose-related flags
                - velocity: Optional movement velocity
                - object_detected: Optional object detection flag
        
        Returns:
            Human-readable description string (1-2 sentences)
        """
        # Get appropriate template function
        template_fn = self.templates.get(rule_name)
        
        if template_fn:
            return template_fn(context)
        else:
            # Fallback for unknown rules
            return self._describe_generic(rule_name, context)
    
    # Template functions for each rule
    
    def _describe_loitering(self, ctx: Dict) -> str:
        """Generate description for loitering rule."""
        person_id = ctx.get('person_id', 'Unknown')
        zone = ctx.get('zone', 'shelf area')
        dwell_time = ctx.get('dwell_time', 0)
        
        # Normalize zone name for readability
        zone_readable = zone.replace('_', ' ').title() if zone else "Shelf Area"
        
        # Time formatting
        if dwell_time < 60:
            time_str = f"{int(dwell_time)} seconds"
        else:
            minutes = int(dwell_time / 60)
            seconds = int(dwell_time % 60)
            time_str = f"{minutes} minute{'s' if minutes != 1 else ''} and {seconds} seconds"
        
        # Generate description with varying templates for natural variety
        templates = [
            f"Person tracked as ID {person_id} remained in the {zone_readable} for {time_str}, exceeding the loitering threshold. Possible concealment or extended browsing behavior detected.",
            f"Track ID {person_id} spent {time_str} in the {zone_readable} without significant movement. Flagged for potential theft-related behavior; review recommended.",
            f"Extended dwell time detected: Person ID {person_id} lingered in {zone_readable} for {time_str}. This may indicate legitimate shopping or possible concealment activity.",
        ]
        
        # Rotate based on time to add variety
        idx = int(time.time()) % len(templates)
        return templates[idx]
    
    def _describe_shelf_exit(self, ctx: Dict) -> str:
        """Generate description for repeated shelf-exit movement."""
        person_id = ctx.get('person_id', 'Unknown')
        repeat_count = ctx.get('repeat_count', 2)
        time_window = ctx.get('time_window', 60)
        
        window_str = f"{int(time_window)} seconds" if time_window < 60 else f"{int(time_window/60)} minutes"
        
        return (f"Person ID {person_id} moved between the shelf area and exit zone "
                f"{repeat_count} times within {window_str}. This back-and-forth pattern "
                f"may indicate indecision, surveillance awareness, or concealment attempts. "
                f"Human review recommended to assess intent.")
    
    def _describe_exit_no_checkout(self, ctx: Dict) -> str:
        """Generate description for exit without checkout."""
        person_id = ctx.get('person_id', 'Unknown')
        visited_shelf = ctx.get('visited_shelf', True)
        
        if visited_shelf:
            return (f"Person ID {person_id} moved from the shelf area directly to the exit "
                    f"without passing through the checkout zone. This path deviation from normal "
                    f"customer flow may indicate unpaid merchandise. Immediate review and possible "
                    f"intervention recommended.")
        else:
            return (f"Person ID {person_id} proceeded to exit without visiting checkout. "
                    f"Possible direct-to-exit behavior flagged for review.")
    
    # Violence/Threat Detection Templates (HIGH PRIORITY)
    
    def _describe_aggressive_pose(self, ctx: Dict) -> str:
        """Generate description for aggressive pose detection."""
        person_id = ctx.get('person_id', 'Unknown')
        pose_type = ctx.get('pose_type', 'raised arms')
        zone = ctx.get('zone', 'store area')
        other_people = ctx.get('nearby_people', 0)
        
        zone_readable = zone.replace('_', ' ').title() if zone else "Store Area"
        
        if other_people > 0:
            return (f"⚠️ HIGH PRIORITY: Person ID {person_id} displaying aggressive postural indicators "
                    f"({pose_type}) in {zone_readable} with {other_people} other individual(s) nearby. "
                    f"Possible altercation developing. Immediate staff presence and de-escalation required. "
                    f"This is a flag for human review, not a confirmed threat.")
        else:
            return (f"⚠️ HIGH PRIORITY: Person ID {person_id} showing aggressive pose indicators "
                    f"({pose_type}) in {zone_readable}. Elevated stress or agitation detected. "
                    f"Staff should approach cautiously to assess situation.")
    
    def _describe_clustering(self, ctx: Dict) -> str:
        """Generate description for rapid clustering/dispersal."""
        num_people = ctx.get('num_people', 3)
        movement_type = ctx.get('movement_type', 'clustering')  # or 'dispersal'
        velocity = ctx.get('avg_velocity', 1.5)
        zone = ctx.get('zone', 'store area')
        
        zone_readable = zone.replace('_', ' ').title() if zone else "Store Area"
        
        if movement_type == 'dispersal':
            return (f"⚠️ HIGH PRIORITY: Sudden dispersal of {num_people} individuals detected in {zone_readable}. "
                    f"People moving rapidly away from a central point (avg velocity: {velocity:.1f} m/s). "
                    f"This pattern often indicates crowd fleeing from a threat. Immediate investigation required.")
        else:
            return (f"⚠️ HIGH PRIORITY: Rapid convergence of {num_people} individuals in {zone_readable}. "
                    f"Sudden clustering behavior detected (avg velocity: {velocity:.1f} m/s). "
                    f"May indicate altercation, medical emergency, or crowd gathering. Staff response needed.")
    
    def _describe_elevated_object(self, ctx: Dict) -> str:
        """Generate description for elevated object detection."""
        person_id = ctx.get('person_id', 'Unknown')
        object_type = ctx.get('object_type', 'long rigid object')
        pose = ctx.get('pose', 'raised')
        zone = ctx.get('zone', 'store area')
        
        zone_readable = zone.replace('_', ' ').title() if zone else "Store Area"
        
        return (f"⚠️ HIGH PRIORITY: Person ID {person_id} in {zone_readable} holding what appears to be "
                f"a {object_type} in a {pose} posture. FLAGGED FOR IMMEDIATE HUMAN REVIEW. "
                f"This is NOT a confirmed weapon detection — object could be store merchandise, "
                f"personal item, or assistive device. Staff should assess from a safe distance and "
                f"contact authorities if threat confirmed.")
    
    def _describe_freeze_posture(self, ctx: Dict) -> str:
        """Generate description for group freeze posture."""
        num_people = ctx.get('num_people', 3)
        duration = ctx.get('duration', 5)
        zone = ctx.get('zone', 'store area')
        
        zone_readable = zone.replace('_', ' ').title() if zone else "Store Area"
        
        return (f"⚠️ HIGH PRIORITY: {num_people} individuals in {zone_readable} exhibiting simultaneous "
                f"static posture for {int(duration)} seconds. This 'freeze' behavior is a common visual "
                f"signature of robbery or hold-up situations where customers/staff stop moving. "
                f"CRITICAL: Staff should NOT approach directly. Contact law enforcement immediately "
                f"if accompanied by other threat indicators.")
    
    def _describe_generic(self, rule_name: str, ctx: Dict) -> str:
        """Fallback description for rules without specific templates."""
        person_id = ctx.get('person_id', 'Unknown')
        zone = ctx.get('zone', 'monitored area')
        timestamp = ctx.get('timestamp', time.strftime("%Y-%m-%d %H:%M:%S"))
        
        return (f"Detection alert: {rule_name} triggered for Person ID {person_id} in {zone} "
                f"at {timestamp}. Review evidence for context and determine appropriate response.")
    
    def get_priority(self, rule_name: str) -> str:
        """
        Determine alert priority based on rule type.
        
        Args:
            rule_name: Name of triggered rule
            
        Returns:
            'high' for violence/threat rules, 'standard' for theft rules
        """
        high_priority_keywords = [
            'aggressive', 'violence', 'threat', 'weapon', 'freeze',
            'clustering', 'dispersal', 'elevated object', 'pose'
        ]
        
        rule_lower = rule_name.lower()
        if any(keyword in rule_lower for keyword in high_priority_keywords):
            return 'high'
        return 'standard'


# Convenience function for quick generation
def generate_description(rule_name: str, context: Dict) -> str:
    """
    Quick helper function to generate a description.
    
    Usage:
        description = generate_description(
            "Loitering in Shelf Zone",
            {
                'person_id': 42,
                'zone': 'shelf',
                'dwell_time': 52,
                'camera_id': 'CAM01'
            }
        )
    """
    generator = DescriptionGenerator()
    return generator.generate(rule_name, context)


# Module-level instance for efficiency (avoid recreating templates)
_default_generator = DescriptionGenerator()


def get_generator() -> DescriptionGenerator:
    """Get the default module-level generator instance."""
    return _default_generator
