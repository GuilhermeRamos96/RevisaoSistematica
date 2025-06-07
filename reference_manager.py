# -*- coding: utf-8 -*-
"""
Reference Management System for PRISMA 2020 Tool
Handles DOI lookup, manual entry, citation tracking, and Vancouver formatting
"""

import re
import requests
from typing import Dict, List, Optional, Any
import json

def extract_doi(input_str: str) -> Optional[str]:
    """Extract DOI from input string using regex pattern"""
    doi_regex = re.compile(r'10.\d{4,9}/[-._;()/:A-Z0-9]+', re.IGNORECASE)
    match = doi_regex.search(input_str)
    return match.group(0) if match else None

def fetch_metadata_from_crossref(doi: str) -> Optional[Dict[str, Any]]:
    """
    Fetch metadata from CrossRef API
    
    Args:
        doi: Digital Object Identifier
        
    Returns:
        Dictionary containing metadata or None if failed
    """
    url = f"https://api.crossref.org/works/{doi}"
    headers = {
        'User-Agent': 'PRISMA-Tool/1.0 (mailto:user@example.com)'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()["message"]
        else:
            print(f"CrossRef API returned status {response.status_code}")
            return None
    except requests.exceptions.Timeout:
        print("Request timeout - CrossRef API took too long to respond")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching DOI metadata: {e}")
        return None
    except Exception as e:
        print(f"Error fetching DOI metadata: {e}")
        return None

def format_vancouver(metadata: Dict[str, Any]) -> str:
    """
    Format reference in Vancouver style from CrossRef metadata
    
    Args:
        metadata: CrossRef metadata dictionary
        
    Returns:
        Formatted reference string
    """
    authors = metadata.get("author", [])
    author_str = ''
    
    for i, author in enumerate(authors):
        family = author.get("family", "")
        given = author.get("given", "")
        initials = ''.join([n[0] + '.' for n in given.split() if n])
        
        if i < 6:
            author_str += f"{family} {initials}, "
        elif i == 6:
            author_str += "et al. "
            break
    
    author_str = author_str.strip().rstrip(',')
    
    title = metadata.get("title", [""])[0] if metadata.get("title") else ""
    journal = metadata.get("container-title", [""])[0] if metadata.get("container-title") else ""
    
    # Extract year from date-parts
    year = ""
    if metadata.get("issued") and metadata["issued"].get("date-parts"):
        year = str(metadata["issued"]["date-parts"][0][0])
    
    volume = metadata.get("volume", "")
    issue = metadata.get("issue", "")
    pages = metadata.get("page", "")
    doi = metadata.get("DOI", "")
    
    # Format reference
    reference_parts = []
    if author_str:
        reference_parts.append(author_str)
    if title:
        reference_parts.append(f"{title}.")
    if journal:
        reference_parts.append(f"{journal}.")
    
    # Year, volume, issue, pages
    if year:
        vol_info = year
        if volume:
            vol_info += f";{volume}"
            if issue:
                vol_info += f"({issue})"
        if pages:
            vol_info += f":{pages}"
        vol_info += "."
        reference_parts.append(vol_info)
    
    if doi:
        reference_parts.append(f"doi:{doi}")
    
    return " ".join(reference_parts)

def format_manual_vancouver(authors: List[str], title: str, journal: str, 
                          year: str, volume: str, issue: str, pages: str, doi: str) -> str:
    """
    Format manual reference in Vancouver style
    
    Args:
        authors: List of author names
        title: Article title
        journal: Journal name
        year: Publication year
        volume: Volume number
        issue: Issue number
        pages: Page range
        doi: DOI
        
    Returns:
        Formatted reference string
    """
    # Format authors
    author_str = ''
    for i, full_name in enumerate(authors):
        full_name = full_name.strip()
        if not full_name:
            continue
            
        parts = full_name.split()
        if len(parts) >= 2:
            family = parts[-1]
            initials = ''.join([n[0] + '.' for n in parts[:-1] if n])
            
            if i < 6:
                author_str += f"{family} {initials}, "
            elif i == 6:
                author_str += "et al. "
                break
    
    author_str = author_str.strip().rstrip(',')
    
    # Build reference
    reference_parts = []
    if author_str:
        reference_parts.append(author_str)
    if title:
        reference_parts.append(f"{title}.")
    if journal:
        reference_parts.append(f"{journal}.")
    
    # Year, volume, issue, pages
    if year:
        vol_info = str(year)
        if volume:
            vol_info += f";{volume}"
            if issue:
                vol_info += f"({issue})"
        if pages:
            vol_info += f":{pages}"
        vol_info += "."
        reference_parts.append(vol_info)
    
    if doi:
        reference_parts.append(f"doi:{doi}")
    
    return " ".join(reference_parts)

class ReferenceManager:
    """
    Comprehensive reference management system
    Handles DOI lookup, manual entry, citation tracking, and reference ordering
    """
    
    def __init__(self):
        self.references: List[Dict[str, Any]] = []
        self.citations: Dict[str, List[int]] = {}  # section_name -> [ref_ids] in citation order
        self.citation_order: List[int] = []  # Global order of first citations
        
    def add_reference_from_doi(self, doi: str) -> Optional[int]:
        """
        Add reference from DOI and return reference ID
        
        Args:
            doi: Digital Object Identifier
            
        Returns:
            Reference ID if successful, None otherwise
        """
        try:
            # Clean and validate DOI input
            clean_doi = doi.strip()
            if not clean_doi:
                print("Empty DOI provided")
                return None
                
            # Try to extract DOI if full URL is provided
            extracted_doi = extract_doi(clean_doi)
            if extracted_doi:
                clean_doi = extracted_doi
            
            print(f"Attempting to fetch metadata for DOI: {clean_doi}")
            metadata = fetch_metadata_from_crossref(clean_doi)
            
            if metadata:
                print("Metadata retrieved successfully")
                formatted_ref = format_vancouver(metadata)
                ref_data = {
                    'id': len(self.references) + 1,
                    'formatted': formatted_ref,
                    'doi': clean_doi,
                    'metadata': metadata,
                    'type': 'doi'
                }
                self.references.append(ref_data)
                print(f"Reference added: ID {ref_data['id']}")
                return ref_data['id']
            else:
                print(f"Could not retrieve metadata for DOI: {clean_doi}")
                return None
                
        except Exception as e:
            print(f"Error adding reference via DOI: {e}")
            import traceback
            traceback.print_exc()
            return None
        
    def add_manual_reference(self, authors: str, title: str, journal: str, 
                           year: str, volume: str = "", issue: str = "", 
                           pages: str = "", doi: str = "") -> Optional[int]:
        """
        Add manual reference and return reference ID
        
        Args:
            authors: Author names (comma-separated)
            title: Article title
            journal: Journal name
            year: Publication year
            volume: Volume number (optional)
            issue: Issue number (optional)
            pages: Page range (optional)
            doi: DOI (optional)
            
        Returns:
            Reference ID if successful, None otherwise
        """
        try:
            # Validate required fields
            if not authors or not title or not journal or not year:
                print("Required fields: authors, title, journal, year")
                return None
                
            # Parse authors
            if isinstance(authors, str):
                # Split by common separators
                author_list = [a.strip() for a in re.split(r'[,;]|and|&', authors) if a.strip()]
            else:
                author_list = authors
            
            print(f"Adding manual reference: {title}")
            formatted_ref = format_manual_vancouver(
                author_list, title, journal, year, volume, issue, pages, doi
            )
            
            ref_data = {
                'id': len(self.references) + 1,
                'formatted': formatted_ref,
                'doi': doi if doi else '',
                'type': 'manual',
                'manual_data': {
                    'authors': author_list,
                    'title': title,
                    'journal': journal,
                    'year': year,
                    'volume': volume,
                    'issue': issue,
                    'pages': pages,
                    'doi': doi
                }
            }
            
            self.references.append(ref_data)
            print(f"Manual reference added: ID {ref_data['id']}")
            return ref_data['id']
            
        except Exception as e:
            print(f"Error adding manual reference: {e}")
            import traceback
            traceback.print_exc()
            return None
        
    def get_reference_by_id(self, ref_id: int) -> Optional[Dict[str, Any]]:
        """Get reference by ID"""
        for ref in self.references:
            if ref['id'] == ref_id:
                return ref
        return None
        
    def get_all_references(self) -> List[Dict[str, Any]]:
        """Get all references sorted by ID"""
        # Ensure all references have required fields
        for ref in self.references:
            if 'type' not in ref:
                ref['type'] = 'manual'  # Default to manual for legacy references
        return sorted(self.references, key=lambda x: x['id'])
        
    def remove_reference(self, ref_id: int) -> bool:
        """
        Remove reference by ID
        
        Args:
            ref_id: Reference ID to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove from references list
            self.references = [ref for ref in self.references if ref['id'] != ref_id]
            
            # Remove from citations
            for section, ref_list in self.citations.items():
                self.citations[section] = [rid for rid in ref_list if rid != ref_id]
            
            # Remove from citation order
            if ref_id in self.citation_order:
                self.citation_order.remove(ref_id)
            
            print(f"Reference {ref_id} removed successfully")
            return True
            
        except Exception as e:
            print(f"Error removing reference {ref_id}: {e}")
            return False
        
    def add_citation(self, section_name: str, ref_id: int):
        """
        Add citation to a section and track global citation order
        
        Args:
            section_name: Name of the section
            ref_id: Reference ID being cited
        """
        # Initialize section citations if not exists
        if section_name not in self.citations:
            self.citations[section_name] = []
        
        # Add to section citations if not already present
        if ref_id not in self.citations[section_name]:
            self.citations[section_name].append(ref_id)
        
        # Track global citation order (only first occurrence)
        if ref_id not in self.citation_order:
            self.citation_order.append(ref_id)
            
    def reorder_references_by_citation(self, sections_content: Dict[str, str] = None):
        """
        Reorder references based on the order they appear in the actual text content
        Updates reference IDs to match citation order of appearance
        
        Args:
            sections_content: Dictionary of section names and their text content
        """
        import re
        
        try:
            if not sections_content:
                print("No sections content provided for reordering")
                return
            
            # Extract all citations from text in order of appearance
            citation_order = []
            
            # Process sections in a logical order (you can customize this)
            section_order = [
                "Título", "Resumo", "Introdução", "Métodos", "Resultados", 
                "Discussão", "Conclusão", "Referências"
            ]
            
            # Add any sections not in the predefined order
            all_sections = list(sections_content.keys())
            for section in all_sections:
                if section not in section_order:
                    section_order.append(section)
            
            # Scan text content for citations in order
            for section_name in section_order:
                if section_name in sections_content:
                    text = sections_content[section_name]
                    # Find all citations [1], [2], [1,2], etc.
                    citations = re.findall(r'\[(\d+(?:,\d+)*)\]', text)
                    
                    for citation in citations:
                        # Handle multiple citations like [1,2,3]
                        ref_ids = [int(id.strip()) for id in citation.split(',')]
                        for ref_id in ref_ids:
                            if ref_id not in citation_order:
                                citation_order.append(ref_id)
            
            print(f"Found citation order: {citation_order}")
            
            # Create mapping of old ID to new ID based on text appearance order
            id_mapping = {}
            new_references = []
            
            # First, add references that appear in text (in order of appearance)
            new_id = 1
            for old_id in citation_order:
                ref = self.get_reference_by_id(old_id)
                if ref:
                    id_mapping[old_id] = new_id
                    new_ref = ref.copy()
                    new_ref['id'] = new_id
                    new_references.append(new_ref)
                    new_id += 1
            
            # Then add uncited references
            for ref in self.references:
                if ref['id'] not in citation_order:
                    id_mapping[ref['id']] = new_id
                    new_ref = ref.copy()
                    new_ref['id'] = new_id
                    new_references.append(new_ref)
                    new_id += 1
            
            # Update references list
            self.references = new_references
            
            # Update all citations in text content with new IDs
            for section, ref_list in self.citations.items():
                self.citations[section] = [id_mapping[old_id] for old_id in ref_list if old_id in id_mapping]
            
            # Update citation order
            self.citation_order = [id_mapping[old_id] for old_id in self.citation_order if old_id in id_mapping]
            
            print("References reordered successfully based on citation order")
            return id_mapping  # Return mapping for text updates
            
        except Exception as e:
            print(f"Error reordering references: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def update_citations_in_text(self, sections_content: Dict[str, str], id_mapping: Dict[int, int]) -> Dict[str, str]:
        """
        Update citation numbers in text content based on ID mapping
        
        Args:
            sections_content: Dictionary of section names and their text content
            id_mapping: Mapping from old IDs to new IDs
            
        Returns:
            Updated sections content with corrected citation numbers
        """
        import re
        
        updated_content = {}
        
        for section_name, text in sections_content.items():
            updated_text = text
            
            # Find all citations and update them
            def replace_citation(match):
                citation_content = match.group(1)  # Content inside brackets
                ref_ids = [int(id.strip()) for id in citation_content.split(',')]
                
                # Map old IDs to new IDs
                new_ids = []
                for old_id in ref_ids:
                    if old_id in id_mapping:
                        new_ids.append(id_mapping[old_id])
                    else:
                        new_ids.append(old_id)  # Keep unmapped IDs as is
                
                # Sort the new IDs and return formatted citation
                new_ids.sort()
                return f"[{','.join(map(str, new_ids))}]"
            
            # Replace all citations in the text
            updated_text = re.sub(r'\[(\d+(?:,\d+)*)\]', replace_citation, updated_text)
            updated_content[section_name] = updated_text
        
        return updated_content
    
    def get_citation_summary(self) -> Dict[str, Any]:
        """
        Get summary of citations across sections
        
        Returns:
            Dictionary with citation statistics
        """
        try:
            total_citations = sum(len(ref_list) for ref_list in self.citations.values())
            unique_references_cited = len(set().union(*self.citations.values())) if self.citations else 0
            sections_with_citations = len([s for s, refs in self.citations.items() if refs])
            
            return {
                'total_citations': total_citations,
                'unique_references_cited': unique_references_cited,
                'total_references': len(self.references),
                'uncited_references': len(self.references) - unique_references_cited,
                'sections_with_citations': sections_with_citations,
                'citation_distribution': {
                    section: len(refs) for section, refs in self.citations.items()
                }
            }
            
        except Exception as e:
            print(f"Error generating citation summary: {e}")
            return {}
    
    def export_references_list(self) -> str:
        """
        Export formatted references list
        
        Returns:
            Formatted string with all references
        """
        try:
            if not self.references:
                return "No references available."
            
            formatted_list = "REFERENCES\n\n"
            
            for ref in self.get_all_references():
                formatted_list += f"{ref['id']}. {ref['formatted']}\n\n"
            
            return formatted_list
            
        except Exception as e:
            print(f"Error exporting references list: {e}")
            return "Error generating references list."
    
    def validate_references(self) -> Dict[str, Any]:
        """
        Validate reference data for completeness and formatting
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'total_references': len(self.references),
            'valid_references': 0,
            'issues': []
        }
        
        try:
            for ref in self.references:
                ref_issues = []
                
                # Check required fields
                if not ref.get('formatted'):
                    ref_issues.append("Missing formatted reference")
                
                if ref.get('type') == 'doi' and not ref.get('doi'):
                    ref_issues.append("DOI reference missing DOI field")
                
                if ref.get('type') == 'manual':
                    manual_data = ref.get('manual_data', {})
                    required_fields = ['authors', 'title', 'journal', 'year']
                    for field in required_fields:
                        if not manual_data.get(field):
                            ref_issues.append(f"Missing {field} in manual reference")
                
                if not ref_issues:
                    validation_results['valid_references'] += 1
                else:
                    validation_results['issues'].append({
                        'ref_id': ref.get('id'),
                        'issues': ref_issues
                    })
            
            validation_results['validation_rate'] = (
                validation_results['valid_references'] / validation_results['total_references']
                if validation_results['total_references'] > 0 else 1.0
            )
            
        except Exception as e:
            validation_results['error'] = str(e)
        
        return validation_results
