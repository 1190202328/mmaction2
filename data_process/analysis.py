import sys
from pprint import pprint

import pandas as pd
import os

parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)

key_value = ['捕食', '跳跃', '走动', '多个动物间的互动']


def get_map_dict(dirs='/home/jjiang/data/项目视频/标注'):
    # 获取原来的数据
    total_class = set()
    for directory in os.listdir(dirs):
        dataset_dir = f'{dirs}/{directory}'
        for file in os.listdir(dataset_dir):
            try:
                data = pd.read_excel(f'{dataset_dir}/{file}', sheet_name='Sheet1')
            except ValueError:
                data = pd.read_excel(f'{dataset_dir}/{file}', sheet_name='16755414')
            try:
                total_class.update(data['label'].tolist())
            except KeyError:
                if file in ['video_info.xlsx', 'video_info(1).xlsx']:
                    continue
                if file == 'F3694 小天鹅房车.xlsx':
                    total_class.update(data['duration_frame'].tolist())
                    continue
                print(f'{dataset_dir}/{file}')
    print('----origin----')
    print(len(total_class))
    print(total_class)
    # 去掉不符规则的数据
    total_class_striped = set()
    for key in total_class:
        if type(key) != str:
            continue
        total_class_striped.add(key.lower().strip())
    print('----striped----')
    print(len(total_class_striped))
    print(total_class_striped)
    # 根据编辑距离对文字进行聚类
    total_class_striped = sorted(list(total_class_striped))
    total_class_clustered_dict = {}
    thresh = 0.5
    from Levenshtein._levenshtein import ratio

    for i in range(len(total_class_striped)):
        if total_class_striped[i] not in total_class_clustered_dict:
            total_class_clustered_dict[total_class_striped[i]] = ''
        for j in range(i + 1, len(total_class_striped)):
            if ratio(total_class_striped[i], total_class_striped[j]) >= thresh and total_class_striped[i] not in ['进食',
                                                                                                                  '捕食'] and \
                    total_class_striped[j] not in ['进食', '捕食']:
                print(total_class_striped[i], total_class_striped[j])
                total_class_clustered_dict[total_class_striped[j]] = total_class_striped[i]
                break
    for key in total_class_clustered_dict:
        value = total_class_clustered_dict[key]
        real_value = ''
        while value != '':
            real_value = value
            value = total_class_clustered_dict[value]
        total_class_clustered_dict[key] = real_value
    total_class_clustered = set()
    for key in total_class_clustered_dict:
        if total_class_clustered_dict[key] == '':
            total_class_clustered.add(key)
        else:
            total_class_clustered.add(total_class_clustered_dict[key])
            # print(f'key: [{key}] value: [{total_class_clustered_dict[key]}]')

    print(f'----clustered thresh={thresh}----')
    print(len(total_class_clustered))
    print(total_class_clustered)

    to_passed_key = {''}

    label = [
        '走动',  # 熊走路
        '老虎走路',  # 老虎走路
        '嬉戏互动',  # 老虎嬉戏
        '嬉戏互动',  # 熊嬉戏
        '嬉戏互动',  # 4 水豚嬉戏
        '进食',  # '猴子进食'
        '嬉戏互动',  # '猴子嬉戏'
        '嬉戏互动',  # '鹿嬉戏'
        '进食',  # 熊进食',
        None,  # '狮子不动',  # 9
        None,  # '狮子小动'
        '走动',  # 狮子走路
        None,  # '猴子不动'
        None,  # 猴子小动
        '走动',  # 14 猴子走路
        '进食',  # '水豚进食'
        None,  # 水豚小动
        '海龟进食',  # '海龟进食'
        None,  # 海龟小动
        None,  # 19 熊小动
        None,  # 狗小动
        '进食',  # '狗进食',
        None,  # 猫小动
        '进食',  # 猫进食',
        None,  # 24 老虎小动
        '进食',  # '老虎进食',
        '进食',  # '鹿进食'
        '进食',  # 捕食
        '跑跳',  # 跳跃
        '嬉戏互动',  # 29
        '走动',  # 30
    ]

    human_dict = {
        '一只棕熊绕岸边走动': label[0],
        '一只熊跑上岸': label[28],
        '一只棕熊用手抓同伴': label[3],
        '一只环尾狐猴跳到同伴身上': label[28],
        '一只老从下方进入在树墩旁与另一只从右上方进入到老虎擦肩而过，各自走出镜头': label[1],
        '一只老虎从下方进入在石台前闻了一下石台上的老虎后走到石台旁站立一会，然后从树墩前绕到树墩后停留，与另一只从右上方进入绕场走出的老虎擦肩而过': label[1],
        '一只老虎从下方进入场地，绕石台左侧走看着树墩后的老虎从右侧走出，它来到树墩后转身往回走，在石台后略停留': label[1],
        '一只老虎从下方进入直奔树墩，跳过树墩扑向树墩后的老虎并抱住，后放开转身跑出镜头。第三只老虎从右上方进入走向树墩后的老虎': label[2],
        '一只老虎从下方进入绕场与右侧进入到老虎擦肩而过，然后停在树墩旁，另一只老虎绕场走出镜头': label[1],
        '一只老虎从前场经过': label[1],
        '一只老虎从右上方进入又转身走出与另一只身后的老虎擦肩而过，后面的老虎绕场走出': label[1],
        '一只老虎从右上方进入，从前场绕出': label[1],
        '一只老虎从右上角进入在树墩后经过躺倒的老虎身边绕前场走出。躺倒的老虎起身观察后又趴下': label[1],
        '一只老虎从右上角进入在树墩旁停留。期间场地左侧的老虎走出镜头和另一只进入走出的老虎擦肩而过': label[1],
        '一只老虎从右上角进入绕树墩后经过躺倒的老虎身边与左侧进入的老虎擦肩而过，分别从石台的左右两侧走出': label[1],
        '一只老虎从右下角走过': label[1],
        '一只老虎从右下角进入绕石台后在树墩旁逗留，期间另一只老虎从左下方进入后又回身走出': label[1],
        '一只老虎从右侧走上石台略观望后趴在石台上': label[1],
        '一只老虎从右侧进入在石台前站住，提留一会后向左侧走出': label[1],
        '一只老虎从右侧进入扒倒在石台旁翻了几个身。另一只老虎随后进入绕到树墩后走出。扒倒的老虎也起身走出': label[1],
        '一只老虎从右侧进入经树墩前绕石台后与左上角进入到老虎擦肩而过后站住。另一只老虎与第三只右上角进入到老虎在树墩后擦肩而过后走出': label[1],
        '一只老虎从右侧进入绕到石台左侧停留观望后走出': label[1],
        '一只老虎从右侧进入绕树墩后在石台后方上到石台与趴着的老虎贴了一下脸后又从石台前下来走出': label[1],
        '一只老虎从右侧进入，经树墩前绕到石台左侧站住并排便。另一只老虎沿着它的路进入在石台后跳上石台并趴下。之前的老虎排完便后走出镜头': label[28],
        '一只老虎从左上方进入绕场走到树墩前停留，方便后转身绕石台后走出。期间另一只老虎从右上方进入，又转回走出': label[1],
        '一只老虎从左上角进入后略停留，然后走到树墩后逗留又转回在石台后停留，后与从下方进入经过前场的老虎先后从左侧走出': label[1],
        '一只老虎从左上角进入绕石台后经树墩前走出。树墩旁的老虎在树墩后徘徊': label[1],
        '一只老虎从左下方进入在石台旁与其它两只老虎相遇，排队向前走。最前的一只老虎趴下伸懒腰，后面两只老虎继续走过它，它突然跃起扑向另两只中的一只，并追赶到前场绕出。第三只还站在树墩后观望': label[1],
        '一只老虎从左下角跳入镜头和另一只老虎跳跃打斗多次然后走出镜头': label[2],
        '一只老虎从左侧进入经前场绕到树墩后略停留后走出，其它两只老虎在左侧场地走动': label[1],
        '一只老虎从左侧进入，绕场走到树墩后躺倒。另一只老虎在左侧场地走动': label[1],
        '一只老虎在左下角站立一会后，看到一只老虎从右侧进入走上石台趴下，它也从石台前绕过走到树墩后与那里的老虎互相闻了两下然后继续绕场到石台后': label[1],
        '一只老虎在树墩后转身绕场走出': label[1],
        '一只老虎站在场地左侧不动，一会后走出镜头': label[1],
        '一只老虎跳起扑向另一只老虎，另一只老虎吓得跑到树墩后躲避': label[2],
        '一只老虎躺倒在地上打滚不起，另一只老虎从它身边走过又走出，第三只老虎跑进又跑出': label[1],
        '一只老虎进入从树墩后绕出再从躺着的老虎身边走过，另一只老虎从左下方进入从石台后绕出': label[1],
        '一只趴在另一身上': None,
        '一狗蹿入': label[28],
        '三只棕熊在休息': label[19],
        '三只老虎一起走到石台左侧，其中两只转身走出，另一只绕石台后走出': label[1],
        '三只老虎先后在场地周围绕场走动，最后有两只老虎分别站住石台后和树墩后': label[1],
        '三只老虎分别绕着场地走动': label[1],
        '三只老虎在场地中略停留，其中两只走出镜头，一只仍站在石台后观望。右上方又有一只老虎进入跳上石台趴下': label[28],
        '三只老虎在场地中追逐，然后慢下来，分开': label[1],
        '两位饲养员走进走出': None,
        '两只场边的老虎突然跳动转身跳出，又分别走进镜头': label[28],
        '两只小猫玩木棍': label[29],
        '两只棕熊互相咬对方': label[3],
        '两只棕熊抱在一起互相撕咬': label[3],
        '两只水豚嬉戏': label[4],
        '两只猴子吃香蕉': label[5],
        '两只环尾狐猴打闹玩耍': label[6],
        '两只老虎从右上角追逐着跑到树墩后互动，第三只老虎跑进来跳到石台上看着他们': label[28],
        '两只老虎从右下角走过': label[1],
        '两只老虎分别从右侧和左下方进入穿过场地从左侧走出，第三只老虎也从右侧进入从左上方走出': label[1],
        '两只老虎分别从场地两侧进入，左边这只在石台后转身往回走出场地，右边这只绕场走出': label[1],
        '两只老虎分别从左下角进入，前面的老虎在场地的左侧停留，后面的老虎从前场经过走出': label[1],
        '两只老虎前后从下方进入在左下角，前面的老虎转身和后面的老虎凶了一下，然后擦肩而过走出': label[1],
        '两只老虎各自走出镜头': label[1],
        '两只老虎在场边走动，一只经过趴着的老虎身边绕场走出': label[1],
        '两只老虎在左下角站立，一只转身从下方走出，一只走到石台上趴下，第三只老虎从左侧进入在石台后转身后从下方走出': label[1],
        '两只老虎擦肩而过后一只从左侧走出，另一只在树墩旁转动后躺倒。第三只老虎从右上角进入': label[1],
        '两只老虎散步': label[1],
        '两只老虎略走动后，树墩后的老虎跳上石台，扑向另一只老虎。两只老虎互扑后分开，仍绕场地走动': label[2],
        '两只老虎顶脑袋嬉戏': label[2],
        '两只鹿互顶': label[7],
        '两熊互动': label[3],
        '之前趴着的老虎起身走向石台走出镜头': label[1],
        '互相蹭头部': label[29],
        '人抱猫': label[29],
        '人狗嬉闹': label[29],
        '仰头': None,
        '仰头 头部转动': None,
        '伸舌头': None,
        '低头啃食': label[27],
        '低头舔前腿': None,
        '侧卧、转动头部': None,
        '侧躺': None,
        '侧躺180度翻转': None,
        '停下张望': None,
        '停落在围栏上': None,
        '关在笼子里的熊': label[19],
        '几只小猫乱爬': None,
        '另一只在树墩旁略停留后走出镜头': label[1],
        '另一只老虎走进画面绕一圈又走出画面': label[1],
        '另一只趴着的老虎也走下石台走出镜头，第三只老虎走进与别的老虎擦肩走过走出镜头，别的老虎也绕场最后走出镜头': label[1],
        '右上方的老虎从前场穿过。石台上的老虎起身趴着': label[1],
        '右下角的老虎就地躺倒': label[24],
        '右下角箱子里海龟爬行': label[18],
        '右侧老虎又转头走出镜头': label[1],
        '吃草': label[27],
        '吃食棕熊转身走动': label[8],
        '后面的老虎在石台后站住，另一只老虎又转身走到石台前。后面的老虎又跳到石台上要扑另一只老虎，但是并没跳下石台，另一只老虎跳出镜头': label[2],
        '回头': None,
        '回头舔身体': None,
        '围栏外有人挂晾衣服': None,
        '坐': None,
        '小熊趴在草地上': label[19],
        '小狮子东张西望': label[10],
        '小狮子低头眯眼': label[10],
        '小狮子向前爬两步': label[11],
        '小狮子咬住奶瓶不松口': label[10],
        '小狮子咬道具，小猴子玩耍': label[10],
        '小狮子四下张望': label[10],
        '小狮子摆动身体': label[10],
        '小狮子甩头': label[10],
        '小狮子睁眼抬头张望': label[10],
        '小狮子翻身': label[10],
        '小狮子舔腿，小猴子玩耍': label[10],
        '小狮子调皮咬玩具': label[10],
        '小狮子走来走去': label[11],
        '小狮子起身': label[10],
        '小狮子趴下': label[10],
        '小狮子躺下': label[10],
        '小狮子闭眼睡觉': label[9],
        '小猴低头挠腿': label[13],
        '小猴啃爪子': label[13],
        '小猴在地上找东西': label[13],
        '小猴在笼子外玩耍': label[13],
        '小猴坐着啃手东张西望': label[13],
        '小猴头拱地': label[13],
        '小猴子玩玩具': label[13],
        '小猴子窜跳': label[28],
        '小猴抓小狮子头': label[13],
        '小猴拽地毯': label[13],
        '小猴捡起香蕉啃食': label[13],
        '小猴掉落': label[13],
        '小猴玩玩具兜': label[13],
        '小猴窜出笼子爬到饲养员身上': label[14],
        '小猴站立': label[12],
        '小猴触碰玩具': label[13],
        '小猴跑到小狮子身上': label[28],
        '小鸟跳动飞走': label[28],
        '岸上的熊在走动': label[0],
        '岸边棕熊观望': label[19],
        '工作人员打扫卫生': None,
        '工作人员用玩具逗狮子': None,
        '左右张望': None,
        '张嘴': None,
        '张嘴 头部转动': None,
        '快步离开': None,
        '戏水': label[3],
        '打哈欠': None,
        '打哈欠 头部转动 舔腿': None,
        '投喂树叶': None,
        '抖动': None,
        '抚摸熊猫': None,
        '抬头': None,
        '抬头 头部转动': None,
        '抬头、转头、低头': None,
        '抱熊': None,
        '挪腿': None,
        '挺起身体抬头': None,
        '摇尾巴 打哈欠 伸懒腰 行走': None,
        '摇尾巴 躺下 行走': None,
        '晃动脑袋': None,
        '树墩后的两只老虎分开，然后先后从场地左侧绕出。石台上的老虎倒退下石台，又从树墩上跨过，再绕场从场地左侧走出': label[1],
        '树墩后的老虎抬掌拍了两下走来的老虎，另一只老虎没理它继续走。两只老虎分别在石台左右停留。': label[1],
        '树墩后的老虎起身走到石台旁，突然跳过石台与刚走出的老虎互扑，然后站住，另一老虎走出.石台上的老虎不停蹭痒': label[2],
        '树墩后的老虎跳过树墩，跃到石台上，扑向石台下的老虎。两只老虎互扑两下后站住场边一会后，一个从石台左边，一个从石台右边进入场地': label[2],
        '树墩后的老虎转身经石台后走出，石台上的老虎舔爪子': label[1],
        '树墩旁的老虎与右上角进入到老虎擦肩而过后从石台前走出，另一只老虎在石台后略逗留后从左侧走出': label[1],
        '树墩旁的老虎绕到石台后走出镜头。场地左右两侧分别进入一只老虎沿场边走动': label[1],
        '检查熊猫头部': None,
        '棕熊休息': label[19],
        '棕熊站起扑倒对方': label[3],
        '棕熊绕圈走': label[0],
        '棕熊观望': label[19],
        '水中两只棕熊站立打闹': label[3],
        '水中和岸边的棕熊嬉戏': label[3],
        '水中玩耍': label[3],
        '水中老虎晃头': label[24],
        '水豚以头蹭地': label[16],
        '水豚侧躺': label[16],
        '水豚后退几步': label[16],
        '水豚在栅栏内外嬉戏': label[4],
        '水豚打滚': label[16],
        '水豚挠痒痒': label[16],
        '水豚晃动身体': label[16],
        '水豚滚动身体': label[16],
        '水豚觅食': label[15],
        '水豚趴下': label[16],
        '水豚跳出木屋': label[28],
        '水豚蹿出栅栏': label[16],
        '水豚躺下': label[16],
        '水豚躺倒蹭地并晃动身体': label[16],
        '水豚转圈坐下': label[16],
        '水豚进入木屋': label[16],
        '水豚逡巡': label[16],
        '海豚趴下': None,
        '海龟交配': label[18],
        '海龟吃食': label[17],
        '海龟挪动身体': label[18],
        '海龟推水豚': label[18],
        '海龟觅食': label[17],
        '海龟转头 爬行 水豚觅食 转头 行走': label[18],
        '游客乘电瓶车进入': None,
        '游客穿行': None,
        '熊互动': label[3],
        '熊作揖': label[3],
        '熊和宝宝亲密接触': label[3],
        '熊喝水': label[8],
        '熊四处乱窜': label[0],
        '熊奔跑': label[28],
        '熊左顾右盼': label[19],
        '熊摔倒': label[19],
        '熊猫吃竹子': label[8],
        '熊猫宝宝打喷嚏': label[19],
        '熊猫抬头': label[19],
        '熊猫晒太阳': label[19],
        '熊猫爬木屋': label[0],
        '熊猫趴下': label[19],
        '熊舔木头': label[19],
        '熊被猴子扑倒': label[6],
        '爬上石头': label[28],
        '狗上课': label[20],
        '狗伸舌头': label[20],
        '狗压跷跷板': label[20],
        '狗叼东西': label[20],
        '狗吃奶': label[21],
        '狗听音乐': label[20],
        '狗咬人': label[20],
        '狗张嘴': label[20],
        '狗打滑梯': label[20],
        '狗抖身体': label[20],
        '狗招手': label[20],
        '狗接飞碟': label[20],
        '狗游泳': label[20],
        '狗直立行走': label[20],
        '狗站课桌左顾右盼、伸舌头、摆头': label[20],
        '狗趴下': label[20],
        '狗跳圈': label[28],
        '狗面对人站立': label[20],
        '狮子侧躺在地上': label[10],
        '狮子回头嚼猴子': label[10],
        '狮子在木箱里打滚': label[10],
        '狮子舔身体': label[10],
        '狮子走动': label[10],
        '狮子趴在地上': label[10],
        '狮子躺着仰头 伸前爪': label[10],
        '猫上窜': label[22],
        '猫举手': label[22],
        '猫伸爪子抓球': label[22],
        '猫低头': label[22],
        '猫做在塑料盆里张望': label[22],
        '猫全神贯注': label[22],
        '猫咀嚼吃鱼': label[23],
        '猫在人背上行走': label[22],
        '猫够食物': label[23],
        '猫挠地': label[22],
        '猫爬进塑料盆': label[22],
        '猫站立': label[22],
        '猫自娱自乐': label[22],
        '猫趴人肩膀上': label[22],
        '猫钻布圈': label[22],
        '猴子互相依偎': label[13],
        '猴子吃水果': label[13],
        '猴子和人亲吻': label[13],
        '猴子咬树叶': label[5],
        '猴子嘴里叼着玩具跳下木箱': label[28],
        '猴子奔跑、散步': label[28],
        '猴子帮猫抓虱子': label[13],
        '猴子挤眉弄眼': label[13],
        '猴子爬铁丝网': label[13],
        '猴子玩尾巴、吃手': label[13],
        '猴子自我欣赏': label[13],
        '猴子茫然四顾': label[13],
        '猴子觅食，边挑边吃': label[5],
        '猴子趴暖气上，左顾右盼': label[13],
        '猴子趴窗台、张嘴': label[13],
        '猴子跳入': label[28],
        '猴子雪地追逐、打闹': label[13],
        '猴崽攀爬': label[13],
        '玩耍 行走 头部转动': label[29],
        '环尾狐猴从小房子上跳下来': label[28],
        '环尾狐猴伸手拍同伴': label[13],
        '环尾狐猴走动 跑跳 俯看 转头': label[28],
        '环尾狐猴转头 咀嚼食物': label[5],
        '用前爪戏水': label[29],
        '石台上的老虎和石台下的老虎互扑，然后分开，一只走出场地，另一只走到树墩后转身几步后躺倒': label[2],
        '石台上的老虎起身下石台，其它两只老虎迅速做出反应，三只老虎在场地内跑动避让，后分开站住观望': label[28],
        '石台上的老虎起身跳下石台从右侧走出，第三只老虎进入在前场转身走出。树墩旁老虎起身经树墩前走出': label[28],
        '石台后的两只老虎先后绕到石台前转身，分别在石台前后站立片刻，再先后从左侧走出': label[1],
        '石台后的老虎突然起身走动，树墩后的老虎也跟着起身扑向石台旁的老虎，石台上的老虎跃起跳开，三只老虎分开': label[2],
        '石台左侧的老虎转身走回，在石台右侧走出，另一只老虎跟随，并在突然跳过石台扑向前面的老虎，然后转身又跑到树墩后': label[28],
        '石台旁的老虎站了会有走出镜头': label[1],
        '石墩旁的老虎向左走出场地，与石台旁向右走的老虎擦肩而过，向右走到老虎在树墩后停留': label[1],
        '站着的老虎看着身边的老虎走动，然后走到石台后和另一只老虎相遇并驻足，另一只老虎绕到石台前，第三只老虎从右侧进入': label[1],
        '站着的老虎绕着石台并沿场地边缘走出。期间另一只老虎从左下方进入又转身走出': label[1],
        '站着的老虎绕石台走到石墩旁躺倒蹭痒': label[1],
        '站着的老虎继续走，绕过树墩走上石台站住观望后趴下打哈欠': label[1],
        '第三只棕熊下水': label[0],
        '第三只老虎从左侧进入': label[1],
        '给狗喂食': label[21],
        '给猫瘙痒': label[22],
        '群熊争食': label[8],
        '群鹿奔跑': label[28],
        '翘起尾巴': None,
        '翻滚': label[29],
        '翻滚 行走 头部转动 跑': label[28],
        '老虎一直趴在石台上休息': label[24],
        '老虎上台阶': label[1],
        '老虎从假山里蹿出': label[1],
        '老虎休憩': label[24],
        '老虎侧躺在地上': label[24],
        '老虎倒退站进水池': label[24],
        '老虎在树林中散步、嬉戏': label[1],
        '老虎在石头上摇头摆尾': label[24],
        '老虎头碰头': label[24],
        '老虎打哈欠': label[24],
        '老虎抖动身体': label[24],
        '老虎摇尾巴': label[24],
        '老虎水池旁散步': label[1],
        '老虎沿场地边缘走出镜头': label[1],
        '老虎洗澡': label[24],
        '老虎甩右前爪': label[24],
        '老虎登上石阶': label[1],
        '老虎绕大树觅食': label[25],
        '老虎趴地刨食': label[25],
        '老虎跃上假山': label[1],
        '老虎蹿树': label[1],
        '老虎进入水池': label[1],
        '老虎驻足仰头': label[24],
        '腿部动作': None,
        '舔前腿': None,
        '舔地': None,
        '舔对方身体': label[29],
        '行走': label[30],
        '行走 低头寻觅': label[30],
        '行走 四处张望': label[30],
        '行走 爬下 头部转动': label[30],
        '行走 起身': label[30],
        '行走 趴下': label[30],
        '行走 躺下': label[30],
        '行走、喝水、打闹、跑': label[28],
        '行走、坐下、低头行走': label[30],
        '行走、张望': label[30],
        '被关起来的熊试图向外探头': label[19],
        '被扑的老虎跑回来直奔树墩后的老虎，它闻闻树墩后的老虎转身要走，后面的老虎又要扑向它，它转身拍了一下，对峙片刻后，先后向场地左侧走去': label[2],
        '角落里的老虎起身走到石台旁跳上石台跑出': label[28],
        '警犬搜毒品': None,
        '走动': label[30],
        '走动的老虎从躺倒的老虎身后绕过走出镜头': label[1],
        '走近水池低头': label[30],
        '起身': None,
        '起身、站立': None,
        '起身站立': None,
        '趴下': None,
        '趴下、站起、趴下、低头': None,
        '趴在地上': None,
        '趴在树墩旁的老虎站起身绕场从左侧走出': label[1],
        '趴在石台上的老虎侧躺下，另一只老虎从左下方进入绕场走出与第三只老虎在右上方擦肩而过': label[1],
        '趴在石台上的老虎起身跳下石台与场边的老虎互扑，然后双双走出镜头': label[2],
        '趴着': None,
        '趴着的老虎打哈欠': label[24],
        '趴着的老虎起身站在石台上观望其它走动的老虎': label[1],
        '趴着老虎用后脚挠痒又在石台上不停的闻': label[24],
        '跑': label[28],
        '跑出老虎又回头扑向石台上的老虎，起身互扑了两次后，跑出老虎跑出镜头，第三只老虎跟着他们绕场跑动也跑出镜头': label[28],
        '蹬腿': None,
        '蹬腿 头部转动': None,
        '身体动作': None,
        '躲在树墩后又在石台后观望，最后走到树墩后的角落里趴下': None,
        '躺下': None,
        '躺下 头部微动 摇尾巴 转身': None,
        '躺倒在石台后的老虎慢慢爬起观望，然后迅速越过石台，扑向场边的另两只老虎': label[2],
        '转头': None,
        '转头、仰头': None,
        '转头舔前腿': None,
        '转身坐下、转动头部': None,
        '进入水池戏水': label[29],
        '陆龟爬行': label[18],
        '饲养员': None,
        '饲养员出现在屏幕右下方': None,
        '饲养员打扫': None,
        '香蕉掉落': None,
        '鹿群雪地觅食': label[26],
        '鹿蹭树': label[7],
        '鹿驻足环顾': label[7],
        '鼓肚子': None,
        '一只棕熊上岸走动': label[0],
        '一只老虎从下方进入从前场走出': label[1],
        '捕食': label[27],
        '跳跃': label[28]
    }

    total_class_human_changed = set()
    total_class_human_changed_not_specific = set()

    for key in total_class_clustered:
        if human_dict.get(key) is not None:
            l = human_dict[key]
            total_class_human_changed.add(l)
        else:
            total_class_human_changed_not_specific.add(key)

    print(f'----total_class_human_changed----')
    print(len(total_class_human_changed))
    print(total_class_human_changed)

    print(f'----total_class_human_changed_not_specific----')
    print(len(total_class_human_changed_not_specific))
    pprint(total_class_human_changed_not_specific)
    return total_class_clustered_dict, human_dict, sorted(list(total_class_human_changed))


def statistics(dirs='/home/jjiang/data/项目视频/标注'):
    total_class_clustered_dict, human_dict = get_map_dict()
    # 统计总的类别下视频数目、视频片段数目
    video_distribution = {}
    video_clip_distribution = {}
    video_clip_distribution_not_include = {}

    for directory in os.listdir(dirs):
        dataset_dir = f'{dirs}/{directory}'
        for file in os.listdir(dataset_dir):
            video_distribution_local = set()
            try:
                data = pd.read_excel(f'{dataset_dir}/{file}', sheet_name='Sheet1')
            except ValueError:
                data = pd.read_excel(f'{dataset_dir}/{file}', sheet_name='16755414')
            try:
                data_local = data['label'].tolist()
            except KeyError:
                if file in ['video_info.xlsx', 'video_info(1).xlsx']:
                    continue
                elif file == 'F3694 小天鹅房车.xlsx':
                    data_local = data['duration_frame'].tolist()
                else:
                    print(f'{dataset_dir}/{file}')
                    raise Exception
            for label in data_local:
                if type(label) != str:
                    continue
                new_label = label.strip().lower()
                new_label = total_class_clustered_dict[new_label] if total_class_clustered_dict[
                                                                         new_label] != "" else new_label
                if human_dict.get(new_label) is None:
                    if new_label not in video_clip_distribution_not_include:
                        video_clip_distribution_not_include[new_label] = 1
                    else:
                        video_clip_distribution_not_include[new_label] += 1
                else:
                    new_label = human_dict[new_label]
                    video_distribution_local.add(new_label)
                    if new_label not in video_clip_distribution:
                        video_clip_distribution[new_label] = 1
                    else:
                        video_clip_distribution[new_label] += 1

            for label in video_distribution_local:
                if label not in video_distribution:
                    video_distribution[label] = 1
                else:
                    video_distribution[label] += 1
    print('------------分析------------')
    print(f'共{len(video_distribution)}类')
    print(f'----视频分布分析----')
    pprint(video_distribution)
    print(f'----视频clip分布分析----')
    pprint(video_clip_distribution)
    print(f'----不在类别中的视频clip分析----')
    pprint(video_clip_distribution_not_include)


def statistics_for_train_test(dirs='/home/jjiang/data/train_test_video'):
    total_class_clustered_dict, human_dict = get_map_dict()
    video_distribution_all = []
    for train_or_test in os.listdir(dirs):
        dataset_dir = f'{dirs}/{train_or_test}'
        # 统计总的类别下视频数目、视频片段数目
        video_distribution = {}
        video_clip_distribution = {}
        video_clip_distribution_not_include = {}
        for file in os.listdir(dataset_dir):
            if not (file.endswith('.xlsx') or file.endswith('.xls')):
                continue
            video_distribution_local = set()
            try:
                data = pd.read_excel(f'{dataset_dir}/{file}', sheet_name='Sheet1')
            except ValueError:
                data = pd.read_excel(f'{dataset_dir}/{file}', sheet_name='16755414')
            try:
                data_local = data['label'].tolist()
            except KeyError:
                if file == 'F3694小天鹅房车.xlsx':
                    data_local = data['duration_frame'].tolist()
                else:
                    print(f'{dataset_dir}/{file}')
                    raise Exception

            for label in data_local:
                if type(label) != str:
                    continue
                new_label = label.strip().lower()
                try:
                    new_label = total_class_clustered_dict[new_label] if total_class_clustered_dict[
                                                                             new_label] != "" else new_label
                except KeyError:
                    print(f'KeyError {new_label}')
                if human_dict.get(new_label) is None:
                    if new_label not in video_clip_distribution_not_include:
                        video_clip_distribution_not_include[new_label] = 1
                    else:
                        video_clip_distribution_not_include[new_label] += 1
                else:
                    new_label = human_dict[new_label]
                    video_distribution_local.add(new_label)
                    if new_label not in video_clip_distribution:
                        video_clip_distribution[new_label] = 1
                    else:
                        video_clip_distribution[new_label] += 1

            for label in video_distribution_local:
                if label not in video_distribution:
                    video_distribution[label] = 1
                else:
                    video_distribution[label] += 1
                if label == '海龟小动':
                    print(f'海龟小动 {file}')
        print(f'------------{train_or_test} 分析------------')
        print(f'共{len(video_distribution)}类')
        print(f'----视频分布分析----')
        pprint(video_distribution)
        print(f'----视频clip分布分析----')
        pprint(video_clip_distribution)
        video_distribution_all.append(video_distribution)
        # print(f'----不在类别中的视频clip分析----')
        # pprint(video_clip_distribution_not_include)
    train_distribution = set(video_distribution_all[0].keys())
    test_distribution = set(video_distribution_all[1].keys())
    print(train_distribution.difference(test_distribution))


if __name__ == '__main__':
    # statistics()
    statistics_for_train_test()
