#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import re
import argparse
import sys
import json

class IntervalComparator:
    def __init__(self):
        self.textgrid_intervals = []
        self.exb_intervals = []
    
    def parse_textgrid(self, textgrid_path, tier_name):
        """
        Parse TextGrid file and extract intervals from specific tier
        
        Args:
            textgrid_path (str): Path to TextGrid file
            tier_name (str): Name of the tier to extract intervals from
        """
        # Try different encodings
        encodings = ['utf-16', 'utf-8', 'utf-16le', 'utf-16be', 'latin1']
        content = None
        
        for encoding in encodings:
            try:
                with open(textgrid_path, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeError:
                continue
            except FileNotFoundError:
                print(f"Error: TextGrid file '{textgrid_path}' not found")
                sys.exit(1)
            except Exception as e:
                print(f"Error reading TextGrid file: {str(e)}")
                sys.exit(1)
                
        if content is None:
            print(f"Error: Could not read TextGrid file with any known encoding")
            sys.exit(1)
        
        # Find the specified tier
        # TextGrid format can have varying whitespace, handle it more flexibly
        tier_pattern = fr'item\s*\[\d+\]:\s*class\s*=\s*"IntervalTier"\s*name\s*=\s*"{tier_name}".*?intervals:\s*size\s*='
        tier_match = re.search(tier_pattern, content, re.DOTALL)
        
        if not tier_match:
            print(f"Error: Tier '{tier_name}' not found in TextGrid file")
            sys.exit(1)
        
        # Extract intervals from the tier
        tier_content = content[tier_match.start():]
        interval_pattern = r'intervals\s*\[\d+\]:\s*xmin\s*=\s*([\d.]+)\s*xmax\s*=\s*([\d.]+)\s*text\s*=\s*"(.*?)"'
        intervals = re.finditer(interval_pattern, tier_content)
        
        for interval in intervals:
            start_time = float(interval.group(1))
            end_time = float(interval.group(2))
            text = interval.group(3)
            
            self.textgrid_intervals.append({
                'start': start_time,
                'end': end_time,
                'text': text
            })
    
    def parse_exb(self, exb_path, category_id):
        """
        Parse EXB file and extract intervals from all tiers in a specific category
        
        Args:
            exb_path (str): Path to EXB file
            category_id (str): Category ID to extract tiers from
        """
        try:
            tree = ET.parse(exb_path)
            root = tree.getroot()
        except FileNotFoundError:
            print(f"Error: EXB file '{exb_path}' not found")
            sys.exit(1)
        except ET.ParseError as e:
            print(f"Error parsing EXB file: {str(e)}")
            sys.exit(1)
        
        # Find timeline
        timeline = {}
        for time in root.findall(".//tli"):
            timeline[time.get('id')] = float(time.get('time', 0))
        
        # Find all tiers in the specified category
        tiers = root.findall(f".//tier[@category='{category_id}']")
        if not tiers:
            print(f"Error: No tiers found in category '{category_id}' in EXB file")
            sys.exit(1)
        
        print(f"Found {len(tiers)} tiers in category '{category_id}'")
        
        # Extract intervals from all matching tiers
        for tier in tiers:
            tier_id = tier.get('id', 'unknown')
            print(f"Processing tier: {tier_id}")
            
            for event in tier.findall('event'):
                start_id = event.get('start')
                end_id = event.get('end')
                text = event.text or ""
                
                try:
                    self.exb_intervals.append({
                        'start': timeline[start_id],
                        'end': timeline[end_id],
                        'text': text,
                        'tier_id': tier_id  # Add tier_id to track which tier it came from
                    })
                except KeyError as e:
                    print(f"Error: Missing timeline entry for event {start_id}-{end_id} in tier {tier_id}")
                    sys.exit(1)
    
    def find_closest_interval(self, target_interval, candidate_intervals):
        """Find the closest interval in time from a list of candidates"""
        if not candidate_intervals:
            return None
            
        # Calculate midpoint of target interval
        target_mid = (target_interval['start'] + target_interval['end']) / 2
        
        # Find closest interval based on midpoint distance
        closest = min(candidate_intervals, 
                     key=lambda x: abs((x['start'] + x['end'])/2 - target_mid))
        
        return closest
    
    def compare_intervals(self, time_tolerance=0.1, text_match_threshold=0.8):
        """
        Compare intervals between TextGrid and EXB files
        
        Args:
            time_tolerance (float): Maximum allowed difference in time boundaries (seconds)
            text_match_threshold (float): Minimum required similarity for text content (0-1)
            
        Returns:
            dict: Comparison results including matching and non-matching intervals
        """
        matches = []
        textgrid_unmatched = []
        exb_unmatched = []
        
        # Helper function to calculate text similarity
        def text_similarity(text1, text2):
            # Extract parts after the first dot
            text1 = text1.lower().strip()
            text2 = text2.lower().strip()
            
            # Split by first dot and take the rest, if no dot present use the whole string
            text1_parts = text1.split('.', 1)
            text2_parts = text2.split('.', 1)
            
            # Get the parts after the dot, or empty string if no dot
            text1_compare = text1_parts[1].strip() if len(text1_parts) > 1 else ""
            text2_compare = text2_parts[1].strip() if len(text2_parts) > 1 else ""
            
            # If both strings are empty after processing, consider them matching
            if not text1_compare and not text2_compare:
                return 1.0
            # If one string is empty after processing, consider them non-matching
            if not text1_compare or not text2_compare:
                return 0.0
                
            # Calculate similarity on the parts after the dot
            common = sum(1 for c in text1_compare if c in text2_compare)
            return 2 * common / (len(text1_compare) + len(text2_compare))
        
        # Compare each TextGrid interval with EXB intervals
        for tg_interval in self.textgrid_intervals:
            found_match = False
            
            for exb_interval in self.exb_intervals:
                # Check time boundaries
                start_diff = abs(tg_interval['start'] - exb_interval['start'])
                end_diff = abs(tg_interval['end'] - exb_interval['end'])
                
                if start_diff <= time_tolerance and end_diff <= time_tolerance:
                    # Check text similarity
                    similarity = text_similarity(tg_interval['text'], exb_interval['text'])
                    
                    if similarity >= text_match_threshold:
                        matches.append({
                            'textgrid': tg_interval,
                            'exb': exb_interval,
                            'time_diff': (start_diff + end_diff) / 2,
                            'text_similarity': similarity
                        })
                        found_match = True
                        break
            
            if not found_match:
                textgrid_unmatched.append(tg_interval)
        
        # Find unmatched EXB intervals
        matched_exb = {m['exb']['start'] for m in matches}
        exb_unmatched = [i for i in self.exb_intervals if i['start'] not in matched_exb]
        
        # Find closest intervals for unmatched entries
        for interval in textgrid_unmatched:
            closest = self.find_closest_interval(interval, self.exb_intervals)
            interval['closest_match'] = closest

        for interval in exb_unmatched:
            closest = self.find_closest_interval(interval, self.textgrid_intervals)
            interval['closest_match'] = closest
        
        return {
            'matches': matches,
            'textgrid_unmatched': textgrid_unmatched,
            'exb_unmatched': exb_unmatched,
            'match_count': len(matches),
            'total_textgrid': len(self.textgrid_intervals),
            'total_exb': len(self.exb_intervals)
        }

def print_results(results, output_format='text'):
    """Print comparison results in specified format"""
    if output_format == 'json':
        print(json.dumps(results, indent=2))
        return

    # Text format output
    print(f"\nComparison Summary:")
    print(f"Total TextGrid intervals: {results['total_textgrid']}")
    print(f"Total EXB intervals: {results['total_exb']}")
    print(f"Matching intervals: {results['match_count']}")
    print(f"Unmatched TextGrid intervals: {len(results['textgrid_unmatched'])}")
    print(f"Unmatched EXB intervals: {len(results['exb_unmatched'])}")
    
    # Print matched intervals
    if results['matches']:
        print("\nMatched Intervals:")
        for match in results['matches']:
            print(f"\nMatch (similarity: {match['text_similarity']:.3f}, time diff: {match['time_diff']:.3f}s)")
            print(f"TextGrid:")
            print(f"  Time: {match['textgrid']['start']:.3f}-{match['textgrid']['end']:.3f}")
            print(f"  Text: {match['textgrid']['text']}")
            print(f"EXB:")
            print(f"  Time: {match['exb']['start']:.3f}-{match['exb']['end']:.3f}")
            print(f"  Text: {match['exb']['text']}")
            if 'tier_id' in match['exb']:
                print(f"  Tier: {match['exb']['tier_id']}")
    
    # Print unmatched intervals
    if results['textgrid_unmatched'] or results['exb_unmatched']:
        print("\nDetailed Mismatches:")
        
        if results['textgrid_unmatched']:
            print("\nUnmatched TextGrid intervals:")
            for interval in results['textgrid_unmatched']:
                print(f"\nTextGrid:")
                print(f"  Time: {interval['start']:.3f}-{interval['end']:.3f}")
                print(f"  Text: {interval['text']}")
                
                if interval.get('closest_match'):
                    closest = interval['closest_match']
                    print(f"Closest EXB match:")
                    print(f"  Time: {closest['start']:.3f}-{closest['end']:.3f}")
                    print(f"  Text: {closest['text']}")
                    if 'tier_id' in closest:
                        print(f"  Tier: {closest['tier_id']}")
                    print(f"  Time difference: {abs((interval['start'] + interval['end'])/2 - (closest['start'] + closest['end'])/2):.3f}s")
        
        if results['exb_unmatched']:
            print("\nUnmatched EXB intervals:")
            for interval in results['exb_unmatched']:
                print(f"\nEXB:")
                print(f"  Time: {interval['start']:.3f}-{interval['end']:.3f}")
                print(f"  Text: {interval['text']}")
                if 'tier_id' in interval:
                    print(f"  Tier: {interval['tier_id']}")
                
                if interval.get('closest_match'):
                    closest = interval['closest_match']
                    print(f"Closest TextGrid match:")
                    print(f"  Time: {closest['start']:.3f}-{closest['end']:.3f}")
                    print(f"  Text: {closest['text']}")
                    print(f"  Time difference: {abs((interval['start'] + interval['end'])/2 - (closest['start'] + closest['end'])/2):.3f}s")

def main():
    parser = argparse.ArgumentParser(
        description='Compare intervals between TextGrid and EXB files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
            Examples:
            %(prog)s input.TextGrid input.exb words tier1
            %(prog)s -t 0.2 -s 0.7 -f json input.TextGrid input.exb words tier1
        '''
    )
    
    parser.add_argument('textgrid', help='Path to TextGrid file')
    parser.add_argument('exb', help='Path to EXB file')
    parser.add_argument('tier_name', help='Name of the tier in TextGrid')
    parser.add_argument('tier_id', help='ID of the tier in EXB')
    parser.add_argument('-t', '--time-tolerance', type=float, default=0.1,
                        help='Time tolerance in seconds (default: 0.1)')
    parser.add_argument('-s', '--similarity-threshold', type=float, default=0.8,
                        help='Text similarity threshold (default: 0.8)')
    parser.add_argument('-f', '--format', choices=['text', 'json'], default='text',
                        help='Output format (default: text)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.time_tolerance < 0:
        parser.error("Time tolerance must be non-negative")
    if not 0 <= args.similarity_threshold <= 1:
        parser.error("Similarity threshold must be between 0 and 1")
    
    # Create comparator and process files
    comparator = IntervalComparator()
    comparator.parse_textgrid(args.textgrid, args.tier_name)
    comparator.parse_exb(args.exb, args.tier_id)
    
    # Compare intervals and print results
    results = comparator.compare_intervals(
        time_tolerance=args.time_tolerance,
        text_match_threshold=args.similarity_threshold
    )
    
    print_results(results, args.format)

if __name__ == '__main__':
    main()