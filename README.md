# BP-SIM
Simulation of blood pressure (BP) measurements taken within a monitoring program.

## Quick Start
Initialize a patient via passing a path to data which contains series of systolic BP (SBP), diastolic BP (DBP), and datetime. A CSV file should be tab-separated (see [examples](https://github.com/Siella/BP-SIM/tree/main/data)). Specify columns to use in a [config file](https://github.com/Siella/BP-SIM/blob/main/config.ini).
```python
p = Patient('PATH-TO-DATA')
```
If you change the attribute `path_to_file`, other [attributes](https://github.com/Siella/BP-SIM/blob/main/meta/classes.png) of the instance `p` will be changed automatically.
```python
print(p.sbp_mean)  # one value
p.path_to_file = 'NEW-PATH-TO-FILE'
print(p.sbp_mean)  # another value
```
Next, pass the patient to `Simulator` and run simulation.
```python
sim = Simulator(p)
sim.run_simulation(100)  # 100 days
```
The result of simulation is stored in `measurements` attribute.
```python
for meas in sim.measurements:
    print(meas.sbp, meas.dbp)
```
Reset results of simulation and run another one.
```python
sim.reset_simulation()
sim.run_simulation(100)
```
To perform information filtering, create rules for measurement processing and initialize `Filter` object.
```python
data = sim.measurements
f = Filter([
            base_rule,
            sd_rule,
            arv_rule,
           ])
f.fit(data)
print(f.apply(data))  # whether an event is a false alert (False) or normal one (True)
```
There are some prepared rules but you can write your own (see [examples](https://github.com/Siella/BP-SIM/blob/main/scripts/rules.py)).

## References
- Nikolaeva K., Elkhovskaya L., Kovalchuk S. Patient measurements simulation and event processing in telemedicine systems // Procedia Computer Science - 2021, Vol. 193, pp. 122-130. https://doi.org/10.1016/j.procs.2021.10.012.
