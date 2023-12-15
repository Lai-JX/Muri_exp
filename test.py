# # import torch
# # from torch import nn
# # class Net(nn.Module):
# #     def __init__(self) -> None:
# #         super().__init__()
# #         # 定义各层
# #         self.model_customize = nn.Sequential(
# #             nn.Conv2d(in_channels=1, out_channels=6, kernel_size=5, stride=1, padding=2),
# #             nn.ReLU(),
# #             nn.MaxPool2d(kernel_size=2),
            
# #             nn.Conv2d(in_channels=6, out_channels=16, kernel_size=5, stride=1, padding=2),
# #             nn.ReLU(),
# #             nn.MaxPool2d(kernel_size=2),
            
# #             nn.Flatten(),
# #             nn.Linear(16*7*7,512),
# #             nn.ReLU(),
# #             nn.Linear(512,10),
# #             # nn.Sigmoid(),
# #             nn.Softmax(dim=1)
# #         )
# #     # 前向传播
# #     def forward(self, x):
# #         x = self.model_customize(x)
# #         return x
import xml.etree.ElementTree as ET     
        
# # if __name__ == '__main__':
# #     net = Net()
# #     print(torch.cuda.is_available())    # True
# #     net = net.cuda()                   
    
# from runtime.rpc_stubs.master_to_worker_pb2 import JobInfo

# import subprocess
# import os
# import utils
# import time


# class Task(object):
#     def __init__(self) -> None:
#         super().__init__()
#         self.log_path='test.txt'

    

#     def get_idle_port(self):
#         return 9013 + 8*min(self._node_id) + int(self._gpus.split(',')[0])
#         # return utils.find_free_port()


#     @staticmethod
#     def test_kill_restart():
#         # bash_cmd = 'sleep 2m'
#         bash_cmd = 'nvidia-smi'
#         return bash_cmd


#     def run(self):
#         cmd = self.test_kill_restart().split()
#         environ_dict = dict(os.environ)
#         environ_dict['CUDA_VISIBLE_DEVICES'] = '0'
#         with open(self.log_path, 'w+') as f:
#             self._handler = subprocess.Popen(
#                 cmd, 
#                 stdout=1,
#                 stderr=2,               # 之后再改为f
#                 env=environ_dict,
#             )

#         return cmd
    

#     def terminate(self):
#         self._handler.terminate()
    
#     def wait(self):
#         self._handler.wait()
    

#     @property
#     def return_code(self):              # 检查进程是否终止，如果终止返回 returncode，否则返回 None
#         return self._handler.poll()

#     @property
#     def pid(self):
#         return self._handler.pid
def parse_xml(filename:str):
    print('parse_xml:',filename)
    fb_memory_usage = []
    utilization = []
    file_content = open(filename, mode='r').read()
    xmls = file_content.split('</nvidia_smi_log>\n')
    for i in range(len(xmls) - 1):
        print(xmls[i])
        root = ET.fromstring(xmls[i] + '</nvidia_smi_log>\n')
        for child in root[4]:
            if child.tag == 'fb_memory_usage':
                fb_memory_usage.append(child[2].text)
            if child.tag == "utilization":
                utilization.append(child[0].text)
    return fb_memory_usage, utilization

if __name__ == '__main__':
    # task = Task()
    # cmd = task.run()
    # print(task.pid)
    # time.sleep(1)
    # task.terminate()
    # task.wait()
    # print(task.return_code)
    # _node_id = [0,1]
    # _num_gpu = 3
    # hostfile_list = [f'gpu{(node_id+1)} slots=2 port=6789\n' for node_id in _node_id]        
    # if 2*len(_node_id) != _num_gpu:
    #     hostfile_list = hostfile_list[0:-1]                                                                             # ljx:需要改为从gpu1开始
    #     hostfile_list.append(f'gpu{(_node_id[-1]+1)} slots={_num_gpu-(len(_node_id)-1)*2} port=6789') 
    print(parse_xml('./workloads/profiling1.xml'))
    print(parse_xml('./workloads/profiling0.xml'))