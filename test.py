# import torch
# from torch import nn
# class Net(nn.Module):
#     def __init__(self) -> None:
#         super().__init__()
#         # 定义各层
#         self.model_customize = nn.Sequential(
#             nn.Conv2d(in_channels=1, out_channels=6, kernel_size=5, stride=1, padding=2),
#             nn.ReLU(),
#             nn.MaxPool2d(kernel_size=2),
            
#             nn.Conv2d(in_channels=6, out_channels=16, kernel_size=5, stride=1, padding=2),
#             nn.ReLU(),
#             nn.MaxPool2d(kernel_size=2),
            
#             nn.Flatten(),
#             nn.Linear(16*7*7,512),
#             nn.ReLU(),
#             nn.Linear(512,10),
#             # nn.Sigmoid(),
#             nn.Softmax(dim=1)
#         )
#     # 前向传播
#     def forward(self, x):
#         x = self.model_customize(x)
#         return x
        
        
# if __name__ == '__main__':
#     net = Net()
#     print(torch.cuda.is_available())    # True
#     net = net.cuda()                   
    
from runtime.rpc_stubs.master_to_worker_pb2 import JobInfo

import subprocess
import os
import utils
import time


class Task(object):
    def __init__(self) -> None:
        super().__init__()
        self.log_path='test.txt'

    

    def get_idle_port(self):
        return 9013 + 8*min(self._node_id) + int(self._gpus.split(',')[0])
        # return utils.find_free_port()


    @staticmethod
    def test_kill_restart():
        # bash_cmd = 'sleep 2m'
        bash_cmd = 'nvidia-smi'
        return bash_cmd


    def run(self):
        cmd = self.test_kill_restart().split()
        environ_dict = dict(os.environ)
        environ_dict['CUDA_VISIBLE_DEVICES'] = '0'
        with open(self.log_path, 'w+') as f:
            self._handler = subprocess.Popen(
                cmd, 
                stdout=1,
                stderr=2,               # 之后再改为f
                env=environ_dict,
            )

        return cmd
    

    def terminate(self):
        self._handler.terminate()
    
    def wait(self):
        self._handler.wait()
    

    @property
    def return_code(self):              # 检查进程是否终止，如果终止返回 returncode，否则返回 None
        return self._handler.poll()

    @property
    def pid(self):
        return self._handler.pid

if __name__ == '__main__':
    task = Task()
    cmd = task.run()
    print(task.pid)
    time.sleep(1)
    task.terminate()
    task.wait()
    print(task.return_code)