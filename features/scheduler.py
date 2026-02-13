from PyQt5 import QtCore
from NOVA.core.base_skill import BaseSkill
from NOVA.core.types import SkillResponse
from NOVA.core.config_manager import config_manager
import threading
import time
import json
import os
import datetime

class SchedulerSkill(QtCore.QObject, BaseSkill):
    # Signal: message, sound_type
    trigger_notification = QtCore.pyqtSignal(str, str)
    
    def __init__(self):
        QtCore.QObject.__init__(self)
        BaseSkill.__init__(self)
        self.name = "SchedulerSkill"
        self.intents = ["set_alarm", "set_reminder"]
        self.description = "Set alarms and reminders."
        self.slots = {
            "time": "Time string (e.g. 5pm, 17:00, 10 minutes)",
            "message": "Content of the reminder"
        }
        
        self.reminders_file = os.path.join(os.path.dirname(__file__), "../config/reminders.json")
        self.running = True
        self.lock = threading.Lock()
        
        # Start Checker Thread
        self.thread = threading.Thread(target=self._check_loop)
        self.thread.daemon = True
        self.thread.start()

    def execute(self, entities: dict) -> SkillResponse:
        time_str = entities.get("time", "")
        message = entities.get("message", "Alarm")
        
        if not time_str:
            return SkillResponse(text="When should I remind you?", success=False)

        # Parse time (Basic implementation, ideally use dateparser)
        # We rely on LLM to give us something reasonable, or simple "X minutes" extraction
        target_time = self._parse_time(time_str)
        
        if not target_time:
             return SkillResponse(text=f"I couldn't understand the time '{time_str}'.", success=False)
             
        self._add_reminder(target_time, message)
        
        display_time = target_time.strftime("%I:%M %p")
        return SkillResponse(text=f"Set reminder for {display_time}: {message}")

    def _parse_time(self, time_str):
        now = datetime.datetime.now()
        time_str = time_str.lower().strip()
        
        # Simple "X minutes"
        if "minute" in time_str:
            try:
                mins = int(time_str.split(" ")[0])
                return now + datetime.timedelta(minutes=mins)
            except:
                pass
        
        # Simple "X seconds"
        if "second" in time_str:
            try:
                secs = int(time_str.split(" ")[0])
                return now + datetime.timedelta(seconds=secs)
            except:
                pass
                
        # Simple "X hours"
        if "hour" in time_str:
            try:
                hrs = int(time_str.split(" ")[0])
                return now + datetime.timedelta(hours=hrs)
            except:
                pass
                
        # Try HH:MM
        try:
             # If strictly HH:MM
             if ":" in time_str:
                 parts = time_str.split(":")
                 h = int(parts[0])
                 m = int(parts[1])
                 target = now.replace(hour=h, minute=m, second=0, microsecond=0)
                 if target < now:
                     target += datetime.timedelta(days=1)
                 return target
        except:
            pass

        return None # Failed to parse

    def _add_reminder(self, dt, msg):
        with self.lock:
            # Load existing
            reminders = []
            if os.path.exists(self.reminders_file):
                try:
                    with open(self.reminders_file, 'r') as f:
                        reminders = json.load(f)
                except:
                    pass
            
            reminders.append({
                "timestamp": dt.timestamp(),
                "message": msg
            })
            
            # Save
            with open(self.reminders_file, 'w') as f:
                json.dump(reminders, f)

    def _check_loop(self):
        while self.running:
            try:
                notify_list = []
                remaining = []
                now_ts = time.time()
                
                with self.lock:
                    if os.path.exists(self.reminders_file):
                         try:
                             with open(self.reminders_file, 'r') as f:
                                 reminders = json.load(f)
                             
                             for r in reminders:
                                 if r["timestamp"] <= now_ts:
                                     notify_list.append(r)
                                 else:
                                     remaining.append(r)
                             
                             if notify_list:
                                 with open(self.reminders_file, 'w') as f:
                                     json.dump(remaining, f)
                         except:
                             pass
                
                # Emit notifications
                for r in notify_list:
                    print(f"TRIGGER REMINDER: {r['message']}")
                    self.trigger_notification.emit(r["message"], "alarm")
                
                time.sleep(5) # Check every 5 seconds
                
            except Exception as e:
                print(f"Scheduler Loop Error: {e}")
                time.sleep(10)
