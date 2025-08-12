import time
from collections import defaultdict


class ActorTimer:
    """Timer class to track different phases of individual actor execution"""
    
    def __init__(self, actor_name):
        self.actor_name = actor_name
        self.phase_times = defaultdict(list)
        self.total_times = defaultdict(float)
        self.start_time = None
        self.phase_start = None
        
    def start_total(self):
        """Start timing the total actor execution"""
        self.start_time = time.time()
        
    def start_phase(self, phase_name):
        """Start timing a specific phase"""
        self.phase_start = time.time()
        
    def end_phase(self, phase_name):
        """End timing a specific phase and record the duration"""
        if self.phase_start is not None:
            duration = time.time() - self.phase_start
            self.phase_times[phase_name].append(duration)
            self.total_times[phase_name] += duration
            self.phase_start = None
            
    def end_total(self):
        """End total timing and return summary"""
        if self.start_time is not None:
            total_duration = time.time() - self.start_time
            return self.generate_summary(total_duration)
        return None
        
    def generate_summary(self, total_duration):
        """Generate timing summary with averages and totals"""
        summary = {
            'actor_name': self.actor_name,
            'total_actor_time': total_duration,
            'phase_breakdown': {},
            'total_phase_times': dict(self.total_times)
        }
        
        for phase, times in self.phase_times.items():
            if times:
                summary['phase_breakdown'][phase] = {
                    'total_time': self.total_times[phase],
                    'average_per_step': sum(times) / len(times),
                    'min_time': min(times),
                    'max_time': max(times),
                    'step_times': times
                }
                
        return summary
        
    def print_summary(self, summary):
        """Print a formatted timing summary for this actor"""
        if not summary:
            return
            
        print("\n" + "="*60)
        print(f"ACTOR TIMING SUMMARY: {self.actor_name}")
        print("="*60)
        print(f"Total actor execution time: {summary['total_actor_time']:.2f} seconds")
        print("\nPhase Breakdown:")
        print("-" * 40)
        
        for phase, stats in summary['phase_breakdown'].items():
            print(f"{phase:20} | Total: {stats['total_time']:8.2f}s | "
                  f"Avg/time_step: {stats['average_per_step']:8.2f}s | "
                  f"Min: {stats['min_time']:6.2f}s | Max: {stats['max_time']:6.2f}s")
        
        print("\nTotal Phase Times:")
        print("-" * 40)
        for phase, total_time in summary['total_phase_times'].items():
            percentage = (total_time / summary['total_actor_time']) * 100
            print(f"{phase:20} | {total_time:8.2f}s ({percentage:5.1f}%)")
        print("="*60 + "\n")
        
        
        

class WorkflowTimer:
    """Timer class to track overall workflow execution and individual actors"""
    
    def __init__(self):
        self.workflow_start_time = None
        self.actor_timings = {}
        self.actor_summaries = {}
        
    def start_workflow(self):
        """Start timing the overall workflow"""
        self.workflow_start_time = time.time()
        print("\n" + "="*60)
        print("STARTING EP STABILITY WORKFLOW")
        print("="*60)
        
    def record_actor_timing(self, actor_name, actor_summary):
        """Record timing information for a specific actor"""
        if actor_summary:
            self.actor_timings[actor_name] = actor_summary['total_actor_time']
            self.actor_summaries[actor_name] = actor_summary
            
    def end_workflow(self):
        """End workflow timing and generate overall summary"""
        if self.workflow_start_time is None:
            return None
            
        total_workflow_time = time.time() - self.workflow_start_time
        return self.generate_workflow_summary(total_workflow_time)
        
    def generate_workflow_summary(self, total_workflow_time):
        """Generate overall workflow timing summary"""
        summary = {
            'total_workflow_time': total_workflow_time,
            'actor_timings': dict(self.actor_timings),
            'actor_summaries': dict(self.actor_summaries),
            'total_actor_time': sum(self.actor_timings.values()),
            'overhead_time': total_workflow_time - sum(self.actor_timings.values())
        }
        return summary
        
    def print_workflow_summary(self, summary):
        """Print the overall workflow timing summary"""
        if not summary:
            return
            
        print("\n" + "="*80)
        print("OVERALL WORKFLOW TIMING SUMMARY")
        print("="*80)
        print(f"Total workflow execution time: {summary['total_workflow_time']:.2f} seconds")
        print(f"Total actor execution time: {summary['total_actor_time']:.2f} seconds")
        print(f"Workflow overhead time: {summary['overhead_time']:.2f} seconds")
        
        if summary['actor_timings']:
            print(f"\nActor Execution Times:")
            print("-" * 50)
            sorted_actors = sorted(summary['actor_timings'].items(), 
                                 key=lambda x: x[1], reverse=True)
            
            for actor_name, actor_time in sorted_actors:
                percentage = (actor_time / summary['total_workflow_time']) * 100
                print(f"{actor_name:20} | {actor_time:8.2f}s ({percentage:5.1f}%)")
                
            print(f"\nDetailed Actor Breakdown:")
            print("-" * 50)
            for actor_name, actor_summary in summary['actor_summaries'].items():
                print(f"\n{actor_name}:")
                for phase, stats in actor_summary['phase_breakdown'].items():
                    print(f"  {phase:20} | {stats['total_time']:8.2f}s | "
                          f"Avg/time_step: {stats['average_per_step']:8.2f}s")
        
        print("="*80 + "\n")