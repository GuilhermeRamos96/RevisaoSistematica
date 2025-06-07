# -*- coding: utf-8 -*-
"""
PRISMA 2020 Flow Diagram Generator
Creates publication-quality PRISMA flow diagrams using matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from typing import Dict, List, Any, Optional
import os

class PRISMADiagram:
    """
    PRISMA 2020 Flow Diagram Generator
    Creates standardized flow diagrams following PRISMA 2020 guidelines
    """
    
    def __init__(self):
        self.fig = None
        self.ax = None
        
    def generate_diagram(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Generate PRISMA 2020 flow diagram
        
        Args:
            data: Dictionary containing flow diagram data
            
        Returns:
            Path to generated diagram image or None if failed
        """
        try:
            # Set up the figure
            self.fig, self.ax = plt.subplots(1, 1, figsize=(12, 16))
            self.ax.set_xlim(0, 12)
            self.ax.set_ylim(0, 20)
            self.ax.axis('off')
            
            # Define colors
            colors = {
                'identification': '#E8F4FD',
                'screening': '#FDF2E9',
                'eligibility': '#EAFDF3',
                'included': '#F0E6FF',
                'border': '#333333',
                'text': '#000000'
            }
            
            # Generate the diagram sections
            self._draw_identification_section(data, colors)
            self._draw_screening_section(data, colors)
            self._draw_eligibility_section(data, colors)
            self._draw_included_section(data, colors)
            
            # Add arrows
            self._draw_arrows()
            
            # Add title
            self.ax.text(6, 19.5, 'PRISMA 2020 Flow Diagram', 
                        ha='center', va='center', fontsize=16, fontweight='bold')
            
            # Save the diagram
            output_path = 'prisma_diagram.png'
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            return output_path
            
        except Exception as e:
            print(f"Error generating PRISMA diagram: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _draw_identification_section(self, data: Dict[str, Any], colors: Dict[str, str]):
        """Draw the Identification section"""
        # Section header
        header_box = FancyBboxPatch(
            (0.5, 16.5), 11, 1.5,
            boxstyle="round,pad=0.1",
            facecolor=colors['identification'],
            edgecolor=colors['border'],
            linewidth=1
        )
        self.ax.add_patch(header_box)
        self.ax.text(6, 17.25, 'Identification', ha='center', va='center', 
                    fontsize=14, fontweight='bold')
        
        # Records identified
        records_box = FancyBboxPatch(
            (1, 14.5), 4.5, 1.5,
            boxstyle="round,pad=0.1",
            facecolor='white',
            edgecolor=colors['border'],
            linewidth=1
        )
        self.ax.add_patch(records_box)
        
        records_text = f"Records identified from:\n"
        records_text += f"Databases (n = {data.get('databases', 0)})\n"
        records_text += f"Registers (n = {data.get('registers', 0)})"
        
        self.ax.text(3.25, 15.25, records_text, ha='center', va='center', 
                    fontsize=10, multialignment='center')
        
        # Records removed before screening
        removed_box = FancyBboxPatch(
            (6.5, 14.5), 4.5, 1.5,
            boxstyle="round,pad=0.1",
            facecolor='white',
            edgecolor=colors['border'],
            linewidth=1
        )
        self.ax.add_patch(removed_box)
        
        removed_text = f"Records removed before screening:\n"
        removed_text += f"Duplicate records removed (n = {data.get('duplicates_removed', 0)})\n"
        removed_text += f"Records marked as ineligible by automation tools (n = {data.get('automation_excluded', 0)})\n"
        removed_text += f"Records removed for other reasons (n = {data.get('other_removed', 0)})"
        
        self.ax.text(8.75, 15.25, removed_text, ha='center', va='center', 
                    fontsize=9, multialignment='center')
    
    def _draw_screening_section(self, data: Dict[str, Any], colors: Dict[str, str]):
        """Draw the Screening section"""
        # Section header
        header_box = FancyBboxPatch(
            (0.5, 11.5), 11, 1,
            boxstyle="round,pad=0.1",
            facecolor=colors['screening'],
            edgecolor=colors['border'],
            linewidth=1
        )
        self.ax.add_patch(header_box)
        self.ax.text(6, 12, 'Screening', ha='center', va='center', 
                    fontsize=14, fontweight='bold')
        
        # Records screened
        screened_box = FancyBboxPatch(
            (1, 9.5), 4.5, 1.5,
            boxstyle="round,pad=0.1",
            facecolor='white',
            edgecolor=colors['border'],
            linewidth=1
        )
        self.ax.add_patch(screened_box)
        self.ax.text(3.25, 10.25, f"Records screened\n(n = {data.get('records_screened', 0)})", 
                    ha='center', va='center', fontsize=10, multialignment='center')
        
        # Records excluded
        excluded_box = FancyBboxPatch(
            (6.5, 9.5), 4.5, 1.5,
            boxstyle="round,pad=0.1",
            facecolor='white',
            edgecolor=colors['border'],
            linewidth=1
        )
        self.ax.add_patch(excluded_box)
        self.ax.text(8.75, 10.25, f"Records excluded\n(n = {data.get('records_excluded', 0)})", 
                    ha='center', va='center', fontsize=10, multialignment='center')
        
        # Reports sought for retrieval
        sought_box = FancyBboxPatch(
            (1, 7.5), 4.5, 1.5,
            boxstyle="round,pad=0.1",
            facecolor='white',
            edgecolor=colors['border'],
            linewidth=1
        )
        self.ax.add_patch(sought_box)
        self.ax.text(3.25, 8.25, f"Reports sought for retrieval\n(n = {data.get('reports_sought', 0)})", 
                    ha='center', va='center', fontsize=10, multialignment='center')
        
        # Reports not retrieved
        not_retrieved_box = FancyBboxPatch(
            (6.5, 7.5), 4.5, 1.5,
            boxstyle="round,pad=0.1",
            facecolor='white',
            edgecolor=colors['border'],
            linewidth=1
        )
        self.ax.add_patch(not_retrieved_box)
        self.ax.text(8.75, 8.25, f"Reports not retrieved\n(n = {data.get('reports_not_retrieved', 0)})", 
                    ha='center', va='center', fontsize=10, multialignment='center')
    
    def _draw_eligibility_section(self, data: Dict[str, Any], colors: Dict[str, str]):
        """Draw the Eligibility section"""
        # Section header
        header_box = FancyBboxPatch(
            (0.5, 5.5), 11, 1,
            boxstyle="round,pad=0.1",
            facecolor=colors['eligibility'],
            edgecolor=colors['border'],
            linewidth=1
        )
        self.ax.add_patch(header_box)
        self.ax.text(6, 6, 'Eligibility', ha='center', va='center', 
                    fontsize=14, fontweight='bold')
        
        # Reports assessed for eligibility
        assessed_box = FancyBboxPatch(
            (1, 3.5), 4.5, 1.5,
            boxstyle="round,pad=0.1",
            facecolor='white',
            edgecolor=colors['border'],
            linewidth=1
        )
        self.ax.add_patch(assessed_box) 
        self.ax.text(3.25, 3.5, f"Reports assessed for eligibility\n(n = {data.get('reports_assessed', 0)})", #aqui
                    ha='center', va='center', fontsize=10, multialignment='center')
        
        # Reports excluded with reasons 
        exclusion_reasons = data.get('exclusion_reasons', [])
        
        # Calculate box height based on number of reasons (minimum 1.5, add 0.3 per reason)
        box_height = max(1.5, 1.0 + len(exclusion_reasons) * 0.35)
        box_y = 4 - box_height/2  # Center the box vertically #aqui
        
        excluded_box = FancyBboxPatch(
            (6.5, box_y), 4.5, box_height,
            boxstyle="round,pad=0.1",
            facecolor='white',
            edgecolor=colors['border'],
            linewidth=1
        )
        self.ax.add_patch(excluded_box)
        
        # Build exclusion text with proper formatting
        exclusion_text = "Reports deleted:\n"
        if exclusion_reasons:
            for reason_data in exclusion_reasons:
                reason = reason_data.get('reason', 'Unknown reason')
                count = reason_data.get('count', 0)
                exclusion_text += f"{reason} (n = {count})\n"
        else:
            # Show placeholder format when no reasons are specified
            exclusion_text += "Reason 1 (n = )\n"
            exclusion_text += "Reason 2 (n = )\n"
            exclusion_text += "Reason 3 (n = )\n"
            exclusion_text += "etc."
        
        # Remove trailing newline
        exclusion_text = exclusion_text.strip()
        
        self.ax.text(8.75, 5, exclusion_text, ha='center', va='center', 
                    fontsize=9, multialignment='center')
    
    def _draw_included_section(self, data: Dict[str, Any], colors: Dict[str, str]):
        """Draw the Included section"""
        # Section header
        header_box = FancyBboxPatch(
            (0.5, 1.5), 11, 1,
            boxstyle="round,pad=0.1",
            facecolor=colors['included'],
            edgecolor=colors['border'],
            linewidth=1
        )
        self.ax.add_patch(header_box)
        self.ax.text(6, 2, 'Included', ha='center', va='center', 
                    fontsize=14, fontweight='bold')
        
        # Studies included in review
        studies_box = FancyBboxPatch(
            (1, 0.25), 4.5, 1,
            boxstyle="round,pad=0.1",
            facecolor='white',
            edgecolor=colors['border'],
            linewidth=1
        )
        self.ax.add_patch(studies_box)
        self.ax.text(3.25, 0.75, f"Studies included in review\n(n = {data.get('studies_included', 0)})", 
                    ha='center', va='center', fontsize=10, multialignment='center')
        
        # Reports of included studies
        reports_box = FancyBboxPatch(
            (6.5, 0.25), 4.5, 1,
            boxstyle="round,pad=0.1",
            facecolor='white',
            edgecolor=colors['border'],
            linewidth=1
        )
        self.ax.add_patch(reports_box)
        self.ax.text(8.75, 0.75, f"Reports of included studies\n(n = {data.get('reports_included', 0)})", 
                    ha='center', va='center', fontsize=10, multialignment='center')
    
    def _draw_arrows(self):
        """Draw connecting arrows between sections"""
        arrow_props = dict(arrowstyle='->', lw=2, color='#333333')
        
        # Identification to Screening
        self.ax.annotate('', xy=(3.25, 11), xytext=(3.25, 14.5), arrowprops=arrow_props)
        
        # Screening internal arrows
        self.ax.annotate('', xy=(3.25, 9), xytext=(3.25, 9.5), arrowprops=arrow_props)
        self.ax.annotate('', xy=(3.25, 7), xytext=(3.25, 7.5), arrowprops=arrow_props)
        
        # Screening to Eligibility
        self.ax.annotate('', xy=(3.25, 5), xytext=(3.25, 7.5), arrowprops=arrow_props)
        
        # Eligibility to Included
        self.ax.annotate('', xy=(3.25, 2.5), xytext=(3.25, 3.5), arrowprops=arrow_props)
        
        # Exclusion arrows (pointing right)
        exclusion_arrow_props = dict(arrowstyle='->', lw=1.5, color='#666666')
        
        # From screened to excluded
        self.ax.annotate('', xy=(6.5, 10.25), xytext=(5.5, 10.25), arrowprops=exclusion_arrow_props)
        
        # From sought to not retrieved
        self.ax.annotate('', xy=(6.5, 8.25), xytext=(5.5, 8.25), arrowprops=exclusion_arrow_props)
        
        # From assessed to excluded
        self.ax.annotate('', xy=(6.5, 4.25), xytext=(5.5, 4.25), arrowprops=exclusion_arrow_props)
    
    def create_sample_diagram(self) -> Optional[str]:
        """
        Create a sample PRISMA diagram with placeholder data
        
        Returns:
            Path to generated diagram image or None if failed
        """
        sample_data = {
            'databases': 1250,
            'registers': 150,
            'duplicates_removed': 200,
            'automation_excluded': 50,
            'other_removed': 25,
            'records_screened': 1125,
            'records_excluded': 900,
            'reports_sought': 225,
            'reports_not_retrieved': 15,
            'reports_assessed': 210,
            'exclusion_reasons': [
                {'reason': 'Did not meet PICOS criteria', 'count': 120},
                {'reason': 'Not peer-reviewed', 'count': 35},
                {'reason': 'Language other than English', 'count': 25},
                {'reason': 'Full text not available', 'count': 10}
            ],
            'studies_included': 20,
            'reports_included': 22
        }
        
        return self.generate_diagram(sample_data)
    
    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate PRISMA diagram data for consistency
        
        Args:
            data: Dictionary containing flow diagram data
            
        Returns:
            Dictionary with validation results and warnings
        """
        warnings = []
        errors = []
        
        try:
            # Check basic flow consistency
            total_identified = data.get('databases', 0) + data.get('registers', 0)
            total_removed = (data.get('duplicates_removed', 0) + 
                           data.get('automation_excluded', 0) + 
                           data.get('other_removed', 0))
            
            expected_screened = total_identified - total_removed
            actual_screened = data.get('records_screened', 0)
            
            if expected_screened != actual_screened:
                warnings.append(
                    f"Records screened ({actual_screened}) doesn't match "
                    f"expected value ({expected_screened}) based on identification and removal data"
                )
            
            # Check screening to eligibility flow
            screened = data.get('records_screened', 0)
            excluded_screening = data.get('records_excluded', 0)
            sought = data.get('reports_sought', 0)
            
            expected_sought = screened - excluded_screening
            if expected_sought != sought:
                warnings.append(
                    f"Reports sought ({sought}) doesn't match "
                    f"expected value ({expected_sought}) based on screening data"
                )
            
            # Check retrieval flow
            not_retrieved = data.get('reports_not_retrieved', 0)
            assessed = data.get('reports_assessed', 0)
            
            expected_assessed = sought - not_retrieved
            if expected_assessed != assessed:
                warnings.append(
                    f"Reports assessed ({assessed}) doesn't match "
                    f"expected value ({expected_assessed}) based on retrieval data"
                )
            
            # Check exclusion reasons total
            exclusion_reasons = data.get('exclusion_reasons', [])
            total_excluded_eligibility = sum(reason.get('count', 0) for reason in exclusion_reasons)
            included = data.get('studies_included', 0)
            
            expected_included = assessed - total_excluded_eligibility
            if expected_included != included:
                warnings.append(
                    f"Studies included ({included}) doesn't match "
                    f"expected value ({expected_included}) based on assessment and exclusion data"
                )
            
        except Exception as e:
            errors.append(f"Error validating data: {str(e)}")
        
        return {
            'valid': len(errors) == 0,
            'warnings': warnings,
            'errors': errors
        }
