### Запуск
сначала скомпилируем нужны файлы
```bash
python setup.py build_ext --inplace
```
Установим количество используемых потоков
```bash
export OMP_NUM_THREADS=4 
```
запуск программы
```bash
python run_conjugate_gradient.py
```
