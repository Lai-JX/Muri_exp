import torch
from torch import nn
class Net(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        # 定义各层
        self.model_customize = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=6, kernel_size=5, stride=1, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),
            
            nn.Conv2d(in_channels=6, out_channels=16, kernel_size=5, stride=1, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),
            
            nn.Flatten(),
            nn.Linear(16*7*7,512),
            nn.ReLU(),
            nn.Linear(512,10),
            # nn.Sigmoid(),
            nn.Softmax(dim=1)
        )
    # 前向传播
    def forward(self, x):
        x = self.model_customize(x)
        return x
        
        
if __name__ == '__main__':
    net = Net()
    print(torch.cuda.is_available())    # True
    net = net.cuda()                    # blocked here
    